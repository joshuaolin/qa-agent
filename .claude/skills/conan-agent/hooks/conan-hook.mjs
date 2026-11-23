import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

class Casebook {
  constructor(dir) {
    this.dir = dir;
  }

  all() {
    if (!fs.existsSync(this.dir)) return [];
    return fs.readdirSync(this.dir)
      .filter((name) => name.endsWith('.md'))
      .sort()
      .reverse()
      .map((name) => this.read(name));
  }

  directives() {
    return this.all().filter((c) => c.type === 'directive');
  }

  latest(count) {
    return this.all().filter((c) => c.type !== 'directive').slice(0, count);
  }

  read(name) {
    const lines = fs.readFileSync(path.join(this.dir, name), 'utf8').split(/\r?\n/);
    const field = (prefix) => {
      const line = lines.find((l) => l.startsWith(prefix));
      return line ? line.slice(prefix.length).trim() : '';
    };
    return { name, type: field('type:'), rule: field('Rule:') };
  }
}

class ConanHook {
  static TRIGGERS = /\b(mali|ulit|bakit|sayang|sira|nasira|fail(ed|s|ing)?|errors?|bug|ulitin|hindi tama|iba (ang )?ibig|di mo nakuha|broken|wrong|incorrect|redo|messed up|not what i (meant|asked|wanted)|that['’]?s not (it|right|what)|does ?n[o'’]t work|did ?n[o'’]t work|not working|still (failing|broken)|why (did|does|is|isn['’]?t)|hindi yan|hindi ganyan|di yan|hindi gumana|di gumana|ayaw gumana)\b/i;
  static LATEST_COUNT = 5;

  constructor(event, casebook) {
    this.event = event;
    this.casebook = casebook;
  }

  async run() {
    const input = await this.readInput();
    const context = this.event === 'session' ? this.sessionContext() : this.promptContext(input.prompt || '');
    if (!context) return;
    process.stdout.write(JSON.stringify({
      hookSpecificOutput: {
        hookEventName: this.event === 'session' ? 'SessionStart' : 'UserPromptSubmit',
        additionalContext: context,
      },
    }));
  }

  readInput() {
    return new Promise((resolve) => {
      let raw = '';
      process.stdin.on('data', (chunk) => { raw += chunk; });
      process.stdin.on('end', () => {
        try { resolve(JSON.parse(raw.replace(/^\uFEFF/, '').trim() || '{}')); } catch { resolve({}); }
      });
    });
  }

  sessionContext() {
    const format = (c) => `- ${c.name}: ${c.rule}`;
    const directives = this.casebook.directives().map(format);
    const latest = this.casebook.latest(ConanHook.LATEST_COUNT).map(format);
    const blocks = [];
    if (directives.length) blocks.push("Josh's standing directives (always apply):", ...directives);
    if (latest.length) blocks.push('conan-agent casebook, latest rules (check before acting in the same area):', ...latest);
    return blocks.join('\n');
  }

  static AGENT_MESSAGE = /<agent-message\b|^Another Claude session sent a message/;

  promptContext(prompt) {
    if (ConanHook.AGENT_MESSAGE.test(prompt)) return '';
    if (!ConanHook.TRIGGERS.test(prompt)) return '';
    return 'conan-agent: this prompt looks like a bug, failure or correction. Load the conan-agent skill: investigate with evidence, search cases/ first, and log the case with its prevention rule once solved.';
  }
}

const skillDir = path.dirname(path.dirname(fileURLToPath(import.meta.url)));
await new ConanHook(process.argv[2], new Casebook(path.join(skillDir, 'cases'))).run();
