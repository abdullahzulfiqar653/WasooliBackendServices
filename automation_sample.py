# import time
# from playwright.sync_api import sync_playwright

# # Replace these with the correct credentials
# username = "3033930338"
# password = "sam123"
# login_url = "http://portal.getlinks.net.pk/login/admin.html"

# if __name__ == "__main__":
#     with sync_playwright() as p:
#         browser = p.chromium.launch(
#             headless=True
#         )  # Set headless=True to run in the background
#         page = browser.new_page()

#         # Open the login page
#         page.goto(login_url)

#         # Wait for the page to be fully loaded before proceeding
#         page.wait_for_load_state("load")  # Ensures page is fully loaded

#         # Fill in the username and password on portal
#         page.fill("//*[@id='access_page']/div/div[4]/form/div[1]/div/input", username)
#         page.fill("//*[@id='access_page']/div/div[4]/form/div[2]/div/input", password)

#         # Click the login button
#         page.click("//*[@id='access_page']/div/div[4]/form/div[3]/div/button")

#         # Wait for the page to be fully loaded after login (page may redirect or load new content)
#         page.wait_for_load_state("load")

#         # Click the specified menu item after logging in on left panel
#         page.click("//*[@id='sidebar-menu']/div/ul/li[5]/a")  # click on Users
#         page.click(
#             "//*[@id='sidebar-menu']/div/ul/li[5]/ul/li[1]/a"
#         )  # click on all users

#         # Wait for the page to be fully loaded after the menu click
#         page.wait_for_load_state("load")  # Wait until the next page is fully loaded

#         # Step 1: Enter a value in the search input
#         page.fill("//*[@id='DataTables_Table_0_filter']/label/input", "3454545653")

#         # Step 2: Click on the search button
#         page.click("//*[@id='searchButton']")

#         # Wait for the search results to load (you can adjust the selector as needed)
#         page.wait_for_load_state("load")

#         # Step 3: Click on the link in the search result to open user detail page
#         page.click("//*[@id='DataTables_Table_0']/tbody/tr/td[4]/a")

#         # Wait for the page to be fully loaded after the new page loads
#         page.wait_for_load_state("load")

#         # Step 4: Click on the renew button that triggers the popup
#         page.locator(
#             "xpath=/html/body/div[2]/div/div[3]/div/div[2]/div/div/div[2]/div[1]/span[2]/a"
#         ).click()

#         # wait for the specific element to be loaded in renew popup so we know popup opened properly
#         page.wait_for_selector(
#             "xpath=/html/body/div[2]/div/div[3]/div/div[2]/div/div/div[2]/form[11]/div/div/div/div[2]/div[9]/div/table/thead/tr/th[1]",
#             timeout=60000,
#         )

#         # Click on the submit button in the renew popup
#         page.locator(
#             "xpath=/html/body/div[2]/div/div[3]/div/div[2]/div/div/div[2]/form[11]/div/div/div/div[3]/button[2]"
#         ).click()

#         # Wait for the popup to disappear or for any changes to reflect
#         page.wait_for_selector(
#             "xpath=/html/body/div[3]", state="detached", timeout=60000
#         )

#         # Read the text from the popup (if needed)
#         fail_text = page.locator("xpath=/html/body/div[3]").inner_text()
#         success_text = page.locator(
#             "xpath=/html/body/div[3]/div/div[2]/div/span"
#         ).inner_text()
#         print(f"Popup Text: {fail_text if fail_text else success_text}")

#         date_of_last_activation = page.locator(
#             "//*[@id='userServerReportTable']/tbody/tr[16]/td[2]"
#         ).inner_text()
#         print("date_of_last_activation: ", date_of_last_activation)

#         # Optional: Print the page title after the action
#         print(page.title())

#         # Close the browser
#         browser.close()
