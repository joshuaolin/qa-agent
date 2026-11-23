const path = require('path');

class TablePainter {
  static STYLE = 'body{font:13px Calibri,Arial;margin:0;background:#fff}#sheet{display:inline-block;padding:12px}h3{margin:0 0 4px}p{margin:0 0 8px;color:#595959}table{border-collapse:collapse}td,th{border:1px solid #999;padding:4px 8px;text-align:left;vertical-align:top;max-width:420px}th{background:#B8CCE4}.pass{background:#C6EFCE}.fail{background:#FFC7CE}';

  constructor(browser, folder) {
    this.browser = browser;
    this.folder = folder;
  }

  escape(value) {
    return String(value).replace(/&/g, '&amp;').replace(/</g, '&lt;');
  }

  resultClass(value) {
    return String(value).split(' ')[0].toLowerCase();
  }

  body(rows) {
    return rows.map(r => `<tr>${r.map((c, i) => `<td class="${i === r.length - 1 ? this.resultClass(c) : ''}">${this.escape(c)}</td>`).join('')}</tr>`).join('');
  }

  async paint(file, title, headers, rows) {
    const page = await this.browser.newPage({ viewport: { width: 1600, height: 400 } });
    const head = `<tr>${headers.map(h => `<th>${this.escape(h)}</th>`).join('')}</tr>`;
    await page.setContent(`<style>${TablePainter.STYLE}</style><div id="sheet"><h3>${this.escape(title)}</h3><p>Captured ${new Date().toISOString()}</p><table>${head}${this.body(rows)}</table></div>`);
    await page.locator('#sheet').screenshot({ path: path.join(this.folder, file) });
    await page.close();
    return file;
  }
}

module.exports = { TablePainter };
