import { test, expect } from '@playwright/test'

test.describe('Portfolio', () => {
  test('loads portfolio page', async ({ page }) => {
    await page.goto('/portfolio')
    await expect(page.getByText('Portfolio')).toBeVisible()
  })

  test('shows add position button', async ({ page }) => {
    await page.goto('/portfolio')
    await expect(page.getByText('Add Position')).toBeVisible()
  })

  test('toggles add position form', async ({ page }) => {
    await page.goto('/portfolio')
    await page.click('text=Add Position')
    await expect(page.getByText('Symbol')).toBeVisible()
    await expect(page.getByText('Quantity')).toBeVisible()
  })

  test('shows empty state when no positions', async ({ page }) => {
    await page.goto('/portfolio')
    await expect(page.getByText(/No positions yet/)).toBeVisible()
  })
})
