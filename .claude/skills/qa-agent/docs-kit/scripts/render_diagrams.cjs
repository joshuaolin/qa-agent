const path = require('path');

const CONFIG = {
  playwright: path.join(process.cwd(), 'node_modules', 'playwright'),
  workDir: path.resolve(process.argv[2] || '.'),
  page: 'diagrams.html',
  viewport: { width: 2000, height: 1600 },
};

class DiagramRenderer {
  constructor(config) {
    this.config = config;
    this.chromium = require(config.playwright).chromium;
  }

  async run() {
    const browser = await this.chromium.launch();
    const page = await browser.newPage({ viewport: this.config.viewport });
    await page.goto('file:///' + path.join(this.config.workDir, this.config.page).replace(/\\/g, '/'));
    for (const card of await page.locator('.card[id]').all()) {
      const id = await card.getAttribute('id');
      const out = path.join(this.config.workDir, `${id}.png`);
      const box = await card.boundingBox();
      await card.screenshot({ path: out, omitBackground: true });
      console.log(`${out} ${Math.round(box.width)}x${Math.round(box.height)}`);
    }
    await browser.close();
  }
}

new DiagramRenderer(CONFIG).run();
