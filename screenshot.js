const puppeteer = require('puppeteer');
const fs = require('fs');

(async () => {
    if (!fs.existsSync('./docs/assets')) fs.mkdirSync('./docs/assets', { recursive: true });

    const browser = await puppeteer.launch({ headless: 'new', defaultViewport: { width: 1440, height: 900 } });
    const page = await browser.newPage();

    await page.goto('http://localhost:5200/', { waitUntil: 'networkidle2' });
    await new Promise(r => setTimeout(r, 2000));

    // Hero
    await page.screenshot({ path: './docs/assets/hero-screenshot.png' });

    // Scroll to IDE
    await page.evaluate(() => document.getElementById('analyzer')?.scrollIntoView({ behavior: 'instant' }));
    await new Promise(r => setTimeout(r, 2000));
    await page.screenshot({ path: './docs/assets/ide-screenshot.png' });

    // Scroll down to see the Analyze + Optimize buttons
    await page.evaluate(() => window.scrollBy(0, 450));
    await new Promise(r => setTimeout(r, 500));
    await page.screenshot({ path: './docs/assets/ide-buttons-screenshot.png' });

    await browser.close();
    console.log('Screenshots saved!');
})();
