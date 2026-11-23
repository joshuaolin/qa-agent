const path = require('path');

class EvidenceShot {
  static MARGIN_Y = 180;
  static STRIP = 'body{margin:0;background:#fff;font:13px Calibri,Arial}#sheet{display:inline-block}.strip{background:#F2F2F2;border-bottom:1px solid #BFBFBF;padding:6px 10px;color:#262626;box-sizing:border-box}.strip b{color:#C00000}.strip .url{font-family:Consolas,monospace;color:#1F4E79;overflow-wrap:anywhere}.strip .meta{color:#595959;white-space:nowrap}img{display:block}';

  constructor(browser, folder) {
    this.browser = browser;
    this.folder = folder;
  }

  escape(value) {
    return String(value).replace(/&/g, '&amp;').replace(/</g, '&lt;');
  }

  async hidePinned(target) {
    await target.evaluate(el => [...document.querySelectorAll('body *')]
      .filter(n => ['fixed', 'sticky'].includes(getComputedStyle(n).position) && !n.contains(el) && !el.contains(n))
      .forEach(n => { n.dataset.qaPinned = n.style.opacity || ' '; n.style.opacity = '0'; }));
  }

  async restore(page) {
    await page.evaluate(() => {
      document.getElementById('qa-evidence-mark')?.remove();
      document.querySelectorAll('[data-qa-pinned]').forEach(n => { n.style.opacity = n.dataset.qaPinned.trim(); delete n.dataset.qaPinned; });
    });
  }

  async mark(target, label) {
    return target.evaluate((el, text) => {
      const box = el.getBoundingClientRect();
      const frame = document.createElement('div');
      frame.id = 'qa-evidence-mark';
      Object.assign(frame.style, { position: 'absolute', left: `${box.left + scrollX - 6}px`, top: `${box.top + scrollY - 6}px`, width: `${box.width + 12}px`, height: `${box.height + 12}px`, border: '3px solid #E00000', borderRadius: '4px', zIndex: 2147483647, pointerEvents: 'none', boxSizing: 'border-box' });
      const tag = document.createElement('div');
      tag.textContent = text;
      Object.assign(tag.style, { position: 'absolute', left: '-3px', top: '-26px', background: '#E00000', color: '#fff', font: 'bold 13px Arial', padding: '3px 8px', borderRadius: '3px', whiteSpace: 'nowrap' });
      frame.appendChild(tag);
      document.body.appendChild(frame);
      return { y: box.top + scrollY, height: box.height };
    }, label);
  }

  region(page, box) {
    const y = Math.max(0, Math.floor(box.y - EvidenceShot.MARGIN_Y - 30));
    return { x: 0, y, width: page.viewportSize().width, height: Math.ceil(box.height + 2 * EvidenceShot.MARGIN_Y + 30) };
  }

  async stamp(file, shot, url, viewport, width) {
    const page = await this.browser.newPage({ viewport: { width: 1600, height: 400 } });
    const meta = `${viewport.width}×${viewport.height} · captured ${new Date().toISOString().replace('T', ' ').slice(0, 16)} UTC`;
    await page.setContent(`<style>${EvidenceShot.STRIP}</style><div id="sheet"><div class="strip" style="width:${Math.max(width, 360)}px"><b>Page URL:</b> <span class="url">${this.escape(url)}</span> <span class="meta">· ${meta}</span></div><img src="data:image/png;base64,${shot.toString('base64')}"></div>`);
    await page.locator('#sheet').screenshot({ path: path.join(this.folder, file) });
    await page.close();
  }

  async capture(page, target, file, label) {
    await target.scrollIntoViewIfNeeded();
    await page.waitForTimeout(600);
    let shot;
    let region;
    try {
      await this.hidePinned(target);
      region = this.region(page, await this.mark(target, label));
      shot = await page.screenshot({ fullPage: true, clip: region });
    } finally {
      await this.restore(page);
    }
    await this.stamp(file, shot, page.url(), page.viewportSize(), region.width);
    return file;
  }
}

module.exports = { EvidenceShot };
