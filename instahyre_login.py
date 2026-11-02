
import os
import re
from pathlib import Path

from dotenv import load_dotenv
from playwright.sync_api import sync_playwright


# ==================================================
# CONFIGURATION
# ==================================================

BASE_DIR = Path(__file__).resolve().parent

load_dotenv(BASE_DIR / ".env")

EMAIL = os.getenv("INSTAHYRE_EMAIL")
PASSWORD = os.getenv("INSTAHYRE_PASSWORD")

LOGIN_URL = "https://www.instahyre.com/login/"

OPPORTUNITIES_URL = (
    "https://www.instahyre.com/candidate/opportunities/"
    "?company_size=0&job_type=0&search=true"
    "&skills=Java,Spring+Boot&years=4"
)

PROFILE_DIR = BASE_DIR / "instahyre_browser_profile"

WAIT_AFTER_APPLY = 3000
CONFIRMATION_TIMEOUT = 4000
NEXT_JOB_TIMEOUT = 20000


# ==================================================
# VALIDATE CREDENTIALS
# ==================================================

if not EMAIL or not PASSWORD:
    raise ValueError("Credentials missing! Check your .env file.")


# ==================================================
# SIMPLE CONSOLE OUTPUT
# ==================================================

def log(message):
    print(message)


# ==================================================
# JOB SIGNATURE
# ==================================================

SIGNATURE_JS = r"""
() => {

    function isVisible(el) {
        const style = window.getComputedStyle(el);
        const rect = el.getBoundingClientRect();

        return (
            style.display !== "none" &&
            style.visibility !== "hidden" &&
            Number(style.opacity) > 0 &&
            rect.width > 0 &&
            rect.height > 0
        );
    }

    function cleanText(el) {
        return (el.innerText || el.textContent || "")
            .replace(/\s+/g, " ")
            .trim();
    }

    const modalElements = Array.from(
        document.querySelectorAll(
            '[role="dialog"], [aria-modal="true"], ' +
            '.modal, .modal-dialog, .modal-content, ' +
            '[class*="modal"]'
        )
    ).filter(isVisible);

    for (const modal of modalElements) {
        const text = cleanText(modal);

        if (text && /\bapply\b/i.test(text)) {
            return text;
        }
    }

    const clickableElements = Array.from(
        document.querySelectorAll(
            'button, a, input[type="button"], ' +
            'input[type="submit"], [role="button"]'
        )
    ).filter(isVisible);

    const applyElements = clickableElements.filter(
        el => /^apply$/i.test(cleanText(el))
    );

    for (const el of applyElements) {

        let parent = el;

        for (let i = 0; i < 10 && parent; i++) {

            const text = cleanText(parent);

            if (
                text.length > 150 &&
                /\bapply\b/i.test(text)
            ) {
                return text;
            }

            parent = parent.parentElement;
        }
    }

    return cleanText(document.body);
}
"""


def get_job_signature(page):
    try:
        return page.evaluate(SIGNATURE_JS)
    except Exception:
        return ""


# ==================================================
# LOGIN
# ==================================================

def login(page):

    log("Login required. Entering credentials...")

    email = page.locator(
        'input[type="email"], input[name="email"], '
        'input[placeholder*="email" i]'
    ).first

    email.wait_for(state="visible", timeout=20000)
    email.fill(EMAIL)

    password = page.locator(
        'input[type="password"]'
    ).first

    password.fill(PASSWORD)

    login_button = page.get_by_role(
        "button",
        name=re.compile(r"log\s*in", re.IGNORECASE)
    ).first

    login_button.click()

    page.wait_for_timeout(5000)

    if "/login/" in page.url.lower():
        input(
            "Complete OTP/CAPTCHA if required. "
            "Press ENTER after successful login..."
        )

    log("Login completed.")


# ==================================================
# FIND APPLY BUTTON
# ==================================================

def get_apply_button(page):

    buttons = page.get_by_role(
        "button",
        name=re.compile(r"^\s*apply\s*$", re.IGNORECASE)
    )

    for i in range(buttons.count()):

        button = buttons.nth(i)

        if button.is_visible() and button.is_enabled():
            return button

    elements = page.get_by_text(
        re.compile(r"^\s*apply\s*$", re.IGNORECASE)
    )

    for i in range(elements.count()):

        element = elements.nth(i)

        if element.is_visible():
            return element

    return None


# ==================================================
# OPTIONAL CONFIRMATION POPUP
# ==================================================

def handle_optional_confirmation(page):

    confirmation_button = page.get_by_role(
        "button",
        name=re.compile(
            r"^\s*apply\s+to\s+\d+\s+jobs?\s*$",
            re.IGNORECASE
        )
    )

    elapsed = 0

    while elapsed < CONFIRMATION_TIMEOUT:

        for i in range(confirmation_button.count()):

            button = confirmation_button.nth(i)

            if button.is_visible() and button.is_enabled():

                log(
                    f"Additional confirmation: "
                    f"{button.inner_text().strip()}"
                )

                button.click(timeout=15000)

                page.wait_for_timeout(2000)

                return True

        page.wait_for_timeout(250)
        elapsed += 250

    return False


# ==================================================
# OPEN FIRST JOB
# ==================================================

def open_first_job(page):

    log("Searching for View job buttons...")

    page.wait_for_timeout(3000)

    view_job = page.get_by_role(
        "link",
        name=re.compile(r"view\s*job", re.IGNORECASE)
    )

    if view_job.count() == 0:

        view_job = page.get_by_role(
            "button",
            name=re.compile(r"view\s*job", re.IGNORECASE)
        )

    if view_job.count() == 0:

        view_job = page.get_by_text(
            re.compile(r"view\s*job", re.IGNORECASE)
        )

    if view_job.count() == 0:
        raise Exception("No View job elements found.")

    log("Opening first job...")

    view_job.first.click(timeout=15000)

    page.wait_for_timeout(3000)

    if get_apply_button(page) is None:
        raise Exception("Apply button not found.")

    log("First job opened successfully.")


# ==================================================
# WAIT FOR NEXT JOB
# ==================================================

def wait_for_next_job(page, previous_signature):

    elapsed = 0

    while elapsed < NEXT_JOB_TIMEOUT:

        page.wait_for_timeout(500)
        elapsed += 500

        current_signature = get_job_signature(page)

        apply_button = get_apply_button(page)

        if (
                current_signature
                and current_signature != previous_signature
                and apply_button is not None
                and apply_button.is_enabled()
        ):

            return True, current_signature

    log("Next job detection timed out.")

    return False, previous_signature


# ==================================================
# CONTINUOUS AUTO-APPLICATION
# ==================================================

def auto_apply(page):

    applied_count = 0

    current_signature = get_job_signature(page)

    log("")
    log("=" * 50)
    log("STARTING INSTAHYRE AUTO-APPLICATION")
    log("Press CTRL + C to stop.")
    log("=" * 50)

    while True:

        apply_button = get_apply_button(page)

        if apply_button is None:
            log("Apply button not found. Stopping.")
            break

        log("")
        log(f"APPLICATION ATTEMPT: {applied_count + 1}")

        try:

            log("Clicking Apply...")

            apply_button.click(timeout=15000)

            log("Apply clicked successfully.")

            page.wait_for_timeout(WAIT_AFTER_APPLY)

            confirmation_clicked = handle_optional_confirmation(
                page
            )

            if confirmation_clicked:
                log("Additional application confirmation completed.")

            applied_count += 1

            log(f"Applications attempted: {applied_count}")

            success, new_signature = wait_for_next_job(
                page,
                current_signature
            )

            if not success:
                log("Stopping automation safely.")
                break

            current_signature = new_signature

            log("Next job detected. Continuing...")

        except KeyboardInterrupt:
            raise

        except Exception as e:
            log(f"Application error: {e}")
            break

    log("")
    log("=" * 50)
    log("APPLICATION SUMMARY")
    log(f"Total application attempts: {applied_count}")
    log("=" * 50)

    return applied_count


# ==================================================
# MAIN
# ==================================================

def main():

    log("Launching Instahyre browser...")

    with sync_playwright() as p:

        context = p.chromium.launch_persistent_context(
            user_data_dir=str(PROFILE_DIR),
            headless=False,
            slow_mo=300,
            args=["--start-maximized"],
            viewport=None
        )

        page = (
            context.pages[0]
            if context.pages
            else context.new_page()
        )

        try:

            # LOGIN

            log("Opening Instahyre...")

            page.goto(
                LOGIN_URL,
                wait_until="domcontentloaded",
                timeout=60000
            )

            page.wait_for_timeout(3000)

            if "/login/" in page.url.lower():

                login(page)

            else:

                log("Existing session detected.")

            # EXPERIENCE FILTER

            log("Applying 4-year experience filter...")

            page.goto(
                OPPORTUNITIES_URL,
                wait_until="domcontentloaded",
                timeout=60000
            )

            page.wait_for_timeout(5000)

            if "experience=4" not in page.url:
                raise Exception("Experience filter not applied.")

            log("Experience filter applied successfully.")

            # OPEN FIRST JOB

            open_first_job(page)

            # AUTO APPLY

            auto_apply(page)

        except KeyboardInterrupt:

            log("\nBot stopped by user.")

        except Exception as e:

            log(f"\nAutomation error: {e}")

        finally:

            log("\nClosing browser...")

            context.close()

            log("Instahyre bot stopped.")


# ==================================================
# ENTRY POINT
# ==================================================

if __name__ == "__main__":
    main()
