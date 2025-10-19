# test_ml_click_escribir.py
# -*- coding: utf-8 -*-
from __future__ import annotations

import time
import pytest
from appium import webdriver
from appium.options.android import UiAutomator2Options
from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

SEARCH_CHIP_ID = "com.mercadolibre:id/ui_components_toolbar_search_field"
SEARCH_INPUT_ID_CANDIDATES = [
    "com.mercadolibre:id/autosuggest_input_search",
    "com.mercadolibre:id/search_input",
    "com.mercadolibre:id/search_bar_input",
    "com.mercadolibre:id/ui_components_search_edit_text",
    "com.mercadolibre:id/ui_components_search_input",
    "com.mercadolibre:id/voice_search_text_input",
]

def wait_clickable(wait, locator):
    return wait.until(EC.element_to_be_clickable(locator))

def ensure_app_foreground(driver, pkg="com.mercadolibre", timeout=10):
    end = time.time() + timeout
    while time.time() < end:
        if driver.current_package == pkg:
            return
        time.sleep(0.25)
    raise AssertionError(f"La app no está en primer plano (current_package={driver.current_package!r})")

def _search_input_visible(wait):
    for rid in SEARCH_INPUT_ID_CANDIDATES:
        try:
            wait.until(EC.element_to_be_clickable((AppiumBy.ID, rid)))
            return True
        except TimeoutException:
            continue
    try:
        wait.until(EC.element_to_be_clickable((
            AppiumBy.ANDROID_UIAUTOMATOR,
            'new UiSelector().className("android.widget.EditText")'
            '.packageName("com.mercadolibre").enabled(true).focusable(true)'
        )))
        return True
    except TimeoutException:
        return False

def safe_tap_search_chip(driver, wait):
    # 1) click normal
    chip = wait_clickable(wait, (AppiumBy.ID, SEARCH_CHIP_ID))
    chip.click()
    time.sleep(0.3)
    if _search_input_visible(wait):
        return True

    # 2) tap por coordenadas (centro) con W3C Actions
    from selenium.webdriver.common.actions.action_builder import ActionBuilder
    from selenium.webdriver.common.actions.pointer_input import PointerInput
    rect = chip.rect
    cx = rect["x"] + rect["width"] // 2
    cy = rect["y"] + rect["height"] // 2
    finger = PointerInput(PointerInput.TOUCH, "finger")
    actions = ActionBuilder(driver, mouse=finger)
    actions.pointer_action.move_to_location(cx, cy)
    actions.pointer_action.pointer_down()
    actions.pointer_action.pause(0.05)
    actions.pointer_action.pointer_up()
    actions.perform()
    time.sleep(0.3)
    if _search_input_visible(wait):
        return True

    # 3) segundo click
    chip.click()
    time.sleep(0.3)
    return _search_input_visible(wait)

def find_search_input(driver, wait):
    for rid in SEARCH_INPUT_ID_CANDIDATES:
        try:
            el = wait_clickable(wait, (AppiumBy.ID, rid))
            print(f"[locator] EditText por ID: {rid}")
            return el
        except TimeoutException:
            pass
    try:
        el = wait_clickable(wait, (AppiumBy.ANDROID_UIAUTOMATOR,
            'new UiSelector().className("android.widget.EditText")'
            '.packageName("com.mercadolibre").enabled(true).focusable(true)'
        ))
        print("[locator] EditText por clase + packageName=com.mercadolibre")
        return el
    except TimeoutException:
        pass
    try:
        el = wait_clickable(wait, (AppiumBy.XPATH, '//android.widget.EditText[@package="com.mercadolibre"]'))
        print("[locator] EditText por XPath + package")
        return el
    except TimeoutException:
        pass
    raise AssertionError("No se encontró el EditText de búsqueda.")

@pytest.fixture
def driver():
    opts = UiAutomator2Options()
    opts.platform_name = "Android"
    opts.automation_name = "UiAutomator2"
    opts.device_name = "AndroidDevice"
    opts.udid = "ad5b164c0601"  # ajusta si es distinto
    opts.app_package = "com.mercadolibre"
    opts.app_activity = "com.mercadolibre.navigation.activities.BottomBarActivity"

    # robustez
    opts.set_capability("appWaitActivity", "*")
    opts.set_capability("adbExecTimeout", 120000)
    opts.set_capability("appWaitDuration", 60000)
    opts.set_capability("appWaitForLaunch", True)
    opts.set_capability("settings[waitForIdleTimeout]", 0)

    # estabilidad
    opts.set_capability("noReset", True)
    opts.set_capability("dontStopAppOnReset", True)
    opts.set_capability("autoGrantPermissions", True)
    opts.set_capability("newCommandTimeout", 180)
    opts.set_capability("skipServerInstallation", True)
    opts.set_capability("ignoreHiddenApiPolicyError", True)

    drv = webdriver.Remote("http://localhost:4723/wd/hub", options=opts)
    yield drv
    drv.quit()

def test_escribir_playstation_5(driver):
    wait = WebDriverWait(driver, 20)
    ensure_app_foreground(driver, "com.mercadolibre", 10)

    # 1) Tap robusto al chip de búsqueda
    assert safe_tap_search_chip(driver, wait), "No se abrió la barra de búsqueda"

    # 2) Escribir "playstation 5"
    search_input = find_search_input(driver, wait)
    search_input.click()
    try:
        search_input.clear()
    except Exception:
        pass
    search_input.send_keys("playstation 5")
