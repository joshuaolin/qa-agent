import datetime
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

import openpyxl
from openpyxl.styles import Alignment, Font, PatternFill

HEAD = Font(name="Calibri", size=10, bold=True)
BODY = Font(name="Calibri", size=10)
LINK = Font(name="Calibri", size=10, color="0563C1", underline="single")
HEAD_FILL = PatternFill("solid", fgColor="B8CCE4")
FILLS = {"PASS": "C6EFCE", "FLAKY": "FFEB9C", "FAIL": "FFC7CE", "INTERRUPTED": "D9D9D9"}


class Run:
    def __init__(self, folder, match, data):
        self.folder = folder
        self.at = datetime.datetime.strptime(match.group(1) + match.group(2), "%Y%m%d%H%M%S")
        self.label = match.group(3)
        self.status = data.get("status", match.group(4))
        self.site = data.get("site", self.label)
        self.attempt = data.get("attempt", 1)
        self.max_attempts = data.get("maxAttempts", 1)
        self.step = data.get("stepReached", "")
        self.remarks = data.get("remarks", "")


class Chain:
    def __init__(self, first):
        self.runs = [first]

    @property
    def outcome(self):
        last = self.runs[-1]
        if last.status == "PASS":
            return "FLAKY" if any(r.status == "FAIL" for r in self.runs) else "PASS"
        return "FAIL" if last.attempt >= last.max_attempts else "INTERRUPTED"


class Signature:
    NUMBERS = re.compile(r"\d{4,}|\d+ms")

    def __init__(self, causes, unknown):
        self.causes = [(re.compile(p, re.I), cause, nxt) for p, cause, nxt in causes]
        self.unknown = tuple(unknown)

    def key(self, run):
        return f"{run.step} | {self.NUMBERS.sub('#', run.remarks)[:160]}"

    def classify(self, run):
        return next(((cause, nxt) for pattern, cause, nxt in self.causes if pattern.search(run.remarks)), self.unknown)


class RunHistory:
    def __init__(self, root, config, since):
        self.config = config
        pattern = re.compile(config["folderPattern"])
        self.runs = []
        for folder in sorted((root / config["runs"]).iterdir()):
            match = pattern.match(folder.name)
            result = folder / "result.json"
            if match and result.exists():
                run = Run(folder, match, json.loads(result.read_text(encoding="utf-8-sig")))
                if not since or run.at.date() >= since:
                    self.runs.append(run)
        if not self.runs:
            raise SystemExit(f"no runs with result.json under {root / config['runs']}" + (f" since {since}" if since else ""))
        self.chains = self.build_chains()

    def build_chains(self):
        chains, open_chain = [], {}
        for run in sorted(self.runs, key=lambda r: r.at):
            current = open_chain.get(run.label)
            gap = (run.at - current.runs[-1].at).total_seconds() / 60 if current else None
            if current and run.attempt > current.runs[-1].attempt and gap <= self.config["chainGapMinutes"]:
                current.runs.append(run)
            else:
                current = Chain(run)
                chains.append(current)
                open_chain[run.label] = current
        return chains

    def same_failure_nearby(self, run, signature):
        window = datetime.timedelta(minutes=self.config["sameBatchMinutes"])
        key = signature.key(run)
        return {r.label for r in self.runs if r.status == "FAIL" and abs(r.at - run.at) <= window and signature.key(r) == key}


class Verdicts:
    def __init__(self, path):
        self.items = json.loads(Path(path).read_text(encoding="utf-8-sig")) if path and Path(path).exists() else []

    def find(self, label, key):
        return next((v for v in self.items if v["label"] == label and v.get("key") == key), None)


class TrendWorkbook:
    def __init__(self, history, signature, verdicts):
        self.history = history
        self.signature = signature
        self.verdicts = verdicts
        self.config = history.config
        self.wb = openpyxl.Workbook()

    def sheet(self, title, headers, widths):
        ws = self.wb.create_sheet(title)
        for i, (h, w) in enumerate(zip(headers, widths), start=1):
            c = ws.cell(row=1, column=i, value=h)
            c.font, c.fill = HEAD, HEAD_FILL
            ws.column_dimensions[openpyxl.utils.get_column_letter(i)].width = w
        ws.freeze_panes = "A2"
        return ws

    def put(self, ws, row, values, fill=None, fill_col=None):
        for i, v in enumerate(values, start=1):
            c = ws.cell(row=row, column=i, value=v)
            c.font, c.alignment = BODY, Alignment(vertical="top", wrap_text=True)
        if fill:
            ws.cell(row=row, column=fill_col).fill = PatternFill("solid", fgColor=FILLS[fill])

    def verdict(self, first, outcomes):
        if sum(outcomes.values()) == outcomes["INTERRUPTED"]:
            return "no completed runs", "INTERRUPTED"
        if first >= self.config["stableFirstTry"]:
            return "stable", "PASS"
        if outcomes["FAIL"] == 0:
            return "flaky: passes on retry", "FLAKY"
        if outcomes["FAIL"] <= self.config["mostlyStableMaxFails"] and first >= self.config["mostlyStableFirstTry"]:
            return "mostly stable: few failed runs", "FLAKY"
        return "unstable: also fails after retries", "FAIL"

    def sites(self):
        ws = self.sheet("Sites", ["Site", "Label", "Scheduled runs", "Passed 1st try", "Flaky (failed, then passed)", "Failed after all retries", "Interrupted (stopped before its retries)", "Attempts used", "Pass 1st try % (completed runs)", "Verdict"], [24, 10, 10, 10, 12, 12, 13, 10, 12, 34])
        groups = defaultdict(list)
        for chain in self.history.chains:
            groups[chain.runs[0].label].append(chain)
        rows = []
        for label, chains in groups.items():
            outcomes = Counter(c.outcome for c in chains)
            completed = len(chains) - outcomes["INTERRUPTED"]
            first = outcomes["PASS"] / completed if completed else 0
            text, fill = self.verdict(first, outcomes)
            rows.append((first, fill, [chains[0].runs[0].site, label, len(chains), outcomes["PASS"], outcomes["FLAKY"], outcomes["FAIL"], outcomes["INTERRUPTED"], sum(len(c.runs) for c in chains), round(first * 100), text]))
        rows.sort(key=lambda r: r[0])
        for n, (_, fill, values) in enumerate(rows, start=2):
            self.put(ws, n, values, fill, 10)
        return rows

    def daily(self):
        days = sorted({c.runs[0].at.date() for c in self.history.chains})
        labels = sorted({c.runs[0].label for c in self.history.chains})
        ws = self.sheet("Daily", ["Label"] + [d.isoformat() for d in days], [10] + [24] * len(days))
        for n, label in enumerate(labels, start=2):
            ws.cell(row=n, column=1, value=label).font = BODY
            for m, day in enumerate(days, start=2):
                chains = [c for c in self.history.chains if c.runs[0].label == label and c.runs[0].at.date() == day]
                if not chains:
                    continue
                text = ", ".join(f"{c.runs[0].at:%H:%M} {c.outcome}" + (f" ({len(c.runs)} tries)" if len(c.runs) > 1 else "") for c in chains)
                cell = ws.cell(row=n, column=m, value=text)
                cell.font, cell.alignment = BODY, Alignment(wrap_text=True, vertical="top")
                worst = next(o for o in ("FAIL", "FLAKY", "INTERRUPTED", "PASS") if any(c.outcome == o for c in chains))
                cell.fill = PatternFill("solid", fgColor=FILLS[worst])

    def failures(self):
        ws = self.sheet("Recurring failures", ["Site", "Step reached", "Failure (numbers masked)", "Times", "Days", "Same failure at other sites, same batch", "Likely cause (from the message)", "Next", "Verdict from evidence (analyst-agent)", "Latest evidence"], [10, 20, 55, 7, 22, 20, 28, 32, 45, 30])
        groups = defaultdict(list)
        for run in self.history.runs:
            if run.status == "FAIL":
                groups[(run.label, self.signature.key(run))].append(run)
        out = []
        for (label, key), runs in sorted(groups.items(), key=lambda g: -len(g[1])):
            latest = runs[-1]
            cause, nxt = self.signature.classify(latest)
            shared = sorted(set().union(*(self.history.same_failure_nearby(r, self.signature) for r in runs)) - {label})
            if len(shared) >= self.config["sharedAtSites"]:
                cause, nxt = f"{cause}; several sites together", "check shared code / environment first (triage step 2)"
            found = self.verdicts.find(label, key)
            sample = runs[:1] + runs[-2:] if len(runs) > 2 else runs
            evidence = next((latest.folder / f.format(label=label) for f in self.config["evidence"] if (latest.folder / f.format(label=label)).exists()), latest.folder)
            out.append({"label": label, "key": key, "step": latest.step, "failure": key.split(" | ", 1)[1], "times": len(runs), "days": ", ".join(sorted({f"{r.at:%m-%d}" for r in runs})), "shared": ", ".join(shared) or "-", "cause": cause, "next": nxt, "verdict": f"{found['verdict']} — {found['evidence']}" if found else "not read yet", "folders": [str(r.folder) for r in sample], "evidence": evidence})
        for n, row in enumerate(out, start=2):
            self.put(ws, n, [row["label"], row["step"], row["failure"], row["times"], row["days"], row["shared"], row["cause"], row["next"], row["verdict"], row["evidence"].name])
            link = ws.cell(row=n, column=10)
            link.hyperlink, link.font = str(row["evidence"]), LINK
        return out

    def save(self, path):
        self.wb.remove(self.wb.active)
        sites = self.sites()
        self.daily()
        failures = self.failures()
        self.wb.move_sheet("Recurring failures", offset=-2)
        if Path(path).exists() and (Path(path).parent / f"~${Path(path).name}").exists():
            raise SystemExit(f"{Path(path).name} is open in Excel; close it first")
        self.wb.save(path)
        return sites, failures


class Analyst:
    def __init__(self, repo, config_file, out, since=None, top=5):
        self.repo = Path(repo).resolve()
        self.config = json.loads(Path(config_file).read_text(encoding="utf-8-sig"))
        self.out = Path(out)
        self.since = datetime.date.fromisoformat(since) if since else None
        self.work = self.repo / "qa-reports" / "analyst"
        self.work.mkdir(parents=True, exist_ok=True)
        suite = self.config["suite"].lower()
        self.brief = self.work / f"{suite}-to-read.json"
        self.verdicts = Verdicts(self.work / f"{suite}-verdicts.json")
        self.top = top

    def run(self):
        history = RunHistory(self.repo, self.config, self.since)
        sites, failures = TrendWorkbook(history, Signature(self.config["causes"], self.config["unknown"]), self.verdicts).save(self.out)
        brief = self.brief
        unread = [f for f in failures if f["verdict"] == "not read yet" and not f["cause"].startswith("run interrupted")][: self.top]
        brief.write_text(json.dumps([{k: f[k] for k in ("label", "key", "step", "failure", "times", "days", "cause", "folders")} for f in unread], ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"{self.config['suite']}: {len(history.runs)} runs, {len(history.chains)} scheduled runs, {history.runs[0].at:%Y-%m-%d} to {history.runs[-1].at:%Y-%m-%d} -> {self.out}")
        for _, _, v in sites[:5]:
            print(f"  {v[1]}: 1st try {v[3]}/{v[2]}, flaky {v[4]}, failed {v[5]}, interrupted {v[6]} - {v[9]}")
        print(f"  recurring failures: {len(failures)}; unclassified: {sum(f['cause'].startswith('unclassified') for f in failures)}; for analyst-agent: {brief}")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    args = dict(a.split("=", 1) for a in sys.argv[4:])
    Analyst(sys.argv[1], sys.argv[2], sys.argv[3], args.get("since"), int(args.get("top", 5))).run()
