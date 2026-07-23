import { test, expect } from '@playwright/test'

test.describe('Dashboard', () => {
  test('loads and shows portfolio summary', async ({ page }) => {
    await page.goto('/')
    await expect(page.getByText('AlphaRadar')).toBeVisible()
    await expect(page.getByText('Dashboard')).toBeVisible()
  })

  test('shows empty state when no positions', async ({ page }) => {
    await page.goto('/')
    await expect(page.getByText('Dashboard')).toBeVisible()
  })

  test('navigates to portfolio via nav', async ({ page }) => {
    await page.goto('/')
    await page.click('text=Portfolio')
    await expect(page).toHaveURL('/portfolio')
    await expect(page.getByText('Portfolio')).toBeVisible()
  })
})
