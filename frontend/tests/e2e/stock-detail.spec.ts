import { test, expect } from '@playwright/test'

test.describe('Stock Detail', () => {
  test('navigates to stock detail from URL', async ({ page }) => {
    await page.goto('/stocks/AAPL')
    await expect(page.getByText('AAPL')).toBeVisible()
  })

  test('shows 404 for invalid symbol', async ({ page }) => {
    await page.goto('/stocks/INVALID')
    await expect(page.getByText('not found')).toBeVisible()
  })

  test('has back navigation', async ({ page }) => {
    await page.goto('/stocks/AAPL')
    await expect(page.getByText('Back')).toBeVisible()
  })
})
