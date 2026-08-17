const { chromium } = require('playwright');
(async () => {
  const browser = await chromium.launch();
  const context = await browser.newContext({
    viewport: { width: 375, height: 800 }
  });
  const page = await context.newPage();
  
  // We need items in the cart to view checkout
  await page.goto('http://127.0.0.1:8000/products/1/');
  await page.waitForTimeout(1000);
  
  // Try to click Add to Cart
  try {
    await page.click('button:has-text("Add to Cart")');
    await page.waitForTimeout(1000);
  } catch(e) {}
  
  // Go to checkout
  await page.goto('http://127.0.0.1:8000/orders/checkout/');
  await page.waitForTimeout(2000);
  
  // Take screenshot
  await page.screenshot({ path: 'mobile_checkout.png', fullPage: true });
  await browser.close();
})();
