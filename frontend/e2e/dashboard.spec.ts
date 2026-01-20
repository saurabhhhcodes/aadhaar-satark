import { test, expect } from '@playwright/test';
import path from 'path';

test.describe('Aadhaar Satark E2E Flow', () => {
    test('should auto-load dashboard and handle extra upload', async ({ page }) => {
        // 1. Load Page
        await page.goto('http://localhost:3001');
        await expect(page).toHaveTitle(/Aadhaar Satark/);

        // 2. Verify Initial Data Loaded (Dashboard Visible)
        // Check for 'Total Pending Updates' stat card or Map
        await expect(page.getByText('Total Pending Updates')).toBeVisible({ timeout: 10000 });
        await expect(page.getByText('Critical Districts')).toBeVisible();

        // 3. Open Upload Modal
        await page.click('button:has-text("Upload Extra Data")');
        await expect(page.getByText('Provide UIDAI CSV extracts')).toBeVisible();

        // 4. Verify Upload Interaction (Optional Mock)
        // const enrolmentFile = path.join(__dirname, 'dummy_enrolment.csv');
        // ...

        // Close modal
        await page.click('button:has-text("Close")', { force: true });
    });
});
