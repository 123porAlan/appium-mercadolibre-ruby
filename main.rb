# test_ml_click_escribir.rb
# -*- coding: utf-8 -*-

require 'appium_lib'
require 'selenium-webdriver'

SEARCH_CHIP_ID = "com.mercadolibre:id/ui_components_toolbar_search_field"
SEARCH_INPUT_ID_CANDIDATES = [
  "com.mercadolibre:id/autosuggest_input_search",
  "com.mercadolibre:id/search_input",
  "com.mercadolibre:id/search_bar_input",
  "com.mercadolibre:id/ui_components_search_edit_text",
  "com.mercadolibre:id/ui_components_search_input",
  "com.mercadolibre:id/voice_search_text_input"
]

def wait_clickable(wait, locator)
  wait.until { |driver| driver.find_element(locator[0], locator[1]).clickable? }
rescue Selenium::WebDriver::Error::TimeoutError
  nil
end

def ensure_app_foreground(driver, pkg = "com.mercadolibre", timeout = 10)
  end_time = Time.now + timeout
  while Time.now < end_time
    return if driver.current_package == pkg
    sleep(0.25)
  end
  raise "La app no está en primer plano (current_package=#{driver.current_package.inspect})"
end

def search_input_visible?(wait)
  SEARCH_INPUT_ID_CANDIDATES.each do |rid|
    begin
      wait.until { |driver| driver.find_element(:id, rid).clickable? }
      return true
    rescue Selenium::WebDriver::Error::TimeoutError
      next
    end
  end

  begin
    wait.until do |driver|
      driver.find_element(
        :uiautomator,
        'new UiSelector().className("android.widget.EditText")' \
        '.packageName("com.mercadolibre").enabled(true).focusable(true)'
      ).clickable?
    end
    return true
  rescue Selenium::WebDriver::Error::TimeoutError
    false
  end
end

def safe_tap_search_chip(driver, wait)
  # 1) click normal
  chip = wait_clickable(wait, [:id, SEARCH_CHIP_ID])
  chip.click
  sleep(0.3)
  return true if search_input_visible?(wait)

  # 2) tap por coordenadas (centro) con W3C Actions
  rect = chip.rect
  cx = rect.x + rect.width / 2
  cy = rect.y + rect.height / 2
  
  finger = Selenium::WebDriver::PointerActions.new(:touch)
  actions = Selenium::WebDriver::ActionBuilder.new(driver, mouse: finger)
  actions.pointer(:touch).move_to_location(cx, cy)
          .pointer_down
          .pause(0.05)
          .pointer_up
  actions.perform
  sleep(0.3)
  return true if search_input_visible?(wait)

  # 3) segundo click
  chip.click
  sleep(0.3)
  search_input_visible?(wait)
end

def find_search_input(driver, wait)
  SEARCH_INPUT_ID_CANDIDATES.each do |rid|
    begin
      el = wait_clickable(wait, [:id, rid])
      puts "[locator] EditText por ID: #{rid}"
      return el
    rescue Selenium::WebDriver::Error::TimeoutError
      next
    end
  end

  begin
    el = wait_clickable(wait, [
      :uiautomator,
      'new UiSelector().className("android.widget.EditText")' \
      '.packageName("com.mercadolibre").enabled(true).focusable(true)'
    ])
    puts "[locator] EditText por clase + packageName=com.mercadolibre"
    return el
  rescue Selenium::WebDriver::Error::TimeoutError
    # continue
  end

  begin
    el = wait_clickable(wait, [:xpath, '//android.widget.EditText[@package="com.mercadolibre"]'])
    puts "[locator] EditText por XPath + package"
    return el
  rescue Selenium::WebDriver::Error::TimeoutError
    # continue
  end

  raise "No se encontró el EditText de búsqueda."
end

def driver
  opts = {
    platformName: "Android",
    automationName: "UiAutomator2",
    deviceName: "AndroidDevice",
    udid: "ad5b164c0601", # ajusta si es distinto
    appPackage: "com.mercadolibre",
    appActivity: "com.mercadolibre.navigation.activities.BottomBarActivity",
    
    # robustez
    appWaitActivity: "*",
    adbExecTimeout: 120000,
    appWaitDuration: 60000,
    appWaitForLaunch: true,
    settings: { waitForIdleTimeout: 0 },
    
    # estabilidad
    noReset: true,
    dontStopAppOnReset: true,
    autoGrantPermissions: true,
    newCommandTimeout: 180,
    skipServerInstallation: true,
    ignoreHiddenApiPolicyError: true
  }

  drv = Appium::Driver.new(caps: opts)
  driver_instance = drv.start_driver
  yield driver_instance
ensure
  driver_instance&.quit
end

def test_escribir_playstation_5(driver)
  wait = Selenium::WebDriver::Wait.new(timeout: 20)
  ensure_app_foreground(driver, "com.mercadolibre", 10)

  # 1) Tap robusto al chip de búsqueda
  raise "No se abrió la barra de búsqueda" unless safe_tap_search_chip(driver, wait)

  # 2) Escribir "playstation 5"
  search_input = find_search_input(driver, wait)
  search_input.click
  begin
    search_input.clear
  rescue StandardError
    # ignore
  end
  search_input.send_keys("playstation 5")
end
