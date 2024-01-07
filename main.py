import time

from selenium import webdriver
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.actions.action_builder import ActionBuilder
from selenium.webdriver.common.actions.mouse_button import MouseButton
from random import randrange
from matplotlib import pyplot as plt
import cv2 as cv
import numpy as np
import pytesseract
import re


def show_mouse(web_driver):
    action = ActionBuilder(web_driver)
    action.pointer_action.pointer_down(MouseButton.MIDDLE)
    action.pointer_action.pointer_up(MouseButton.MIDDLE)
    action.perform()
    time.sleep(2)
    action.perform()


def move_mouse(web_driver, pos):
    action = ActionBuilder(web_driver)
    action.pointer_action.move_to_location(pos[0], pos[1])
    action.perform()


def click_mouse(web_driver, target):
    move_mouse(driver, target)
    time.sleep(1)
    time.sleep(randrange(1, 5, 1) / 10)
    action = ActionBuilder(web_driver)
    action.pointer_action.pointer_down(MouseButton.LEFT)
    action.perform()
    time.sleep(randrange(1, 5, 1) / 100)
    action.clear_actions()
    action.pointer_action.pointer_up(MouseButton.LEFT)
    action.perform()


def find_template_center_in_current_screen(driver, template_name):
    driver.save_screenshot("curr.png")
    template = cv.imread(template_name, 1)
    w, h = template.shape[1::-1]
    res = cv.matchTemplate(cv.imread("curr.png", 1), template, cv.TM_CCOEFF)
    min_val, max_val, min_loc, max_loc = cv.minMaxLoc(res)
    print(template_name, min_val, max_val)
    top_left = max_loc
    bottom_right = (top_left[0] + w, top_left[1] + h)
    return get_center(top_left, bottom_right)


def get_center(top_left, bottom_right):
    return np.add(top_left, np.subtract(np.array(bottom_right), np.array(top_left)) / 2)


def accept_cookie_banner(driver):
    cookieAccept = driver.find_element(By.ID, 'didomi-notice-agree-button')
    ActionChains(driver).click(cookieAccept).perform()


def perform_login(driver, username, password):
    ActionChains(driver) \
        .send_keys(username) \
        .pause(1) \
        .key_down(Keys.TAB) \
        .pause(randrange(1, 5, 1) / 10) \
        .key_up(Keys.TAB) \
        .pause(1) \
        .send_keys(password) \
        .pause(randrange(1, 5, 1) / 10) \
        .key_down(Keys.RETURN) \
        .pause(randrange(1, 5, 1) / 10) \
        .key_up(Keys.RETURN) \
        .perform()


def load_game(driver):
    driver.get('https://sfgame.net/')

    accept_cookie_banner(driver)

    # login
    loginButton = driver.find_element(By.ID, 'cta')
    ActionChains(driver).click(loginButton).perform()
    # wait for game load
    time.sleep(15)

    # target = find_template_center_in_current_screen(driver, "template/login_upscaled.png")
    click_mouse(driver, (1217.5, 950.5))

    time.sleep(2)
    perform_login(driver, "user", "pass")
    time.sleep(5)

    # target = find_template_center_in_current_screen(driver, "template/eu_9.png")
    click_mouse(driver, (1219.5, 385.5))

    time.sleep(5)


def prepareImageForTavernStateTextReadout(src):
    copy = src
    white = np.array([255, 255, 255])
    white_lo = np.array([184, 182, 180])
    white_mask = cv.inRange(copy, white_lo, white)
    copy[white_mask == 0] = (0, 0, 0)
    return copy


def prepareImageForQuestTextReadout(src):
    copy = src

    event_hi = np.array([255, 88, 208])
    event_lo = np.array([255, 88, 208])
    event_mask = cv.inRange(copy, event_lo, event_hi)
    copy[event_mask > 0] = (255, 255, 255)

    white = np.array([255, 255, 255])
    white_lo = np.array([240, 240, 240])
    white_mask = cv.inRange(copy, white_lo, white)
    copy[white_mask == 0] = (0, 0, 0)
    return copy


def read_thirst_for_adv(driver):
    driver.save_screenshot('curr.png')
    current_screen = cv.imread('curr.png')
    # start row:end row, start col:end col
    cropped = current_screen[850:928, 960:1318]
    modified = prepareImageForTavernStateTextReadout(cropped)
    ret, th1 = cv.threshold(modified, 127, 255, cv.THRESH_BINARY_INV)
    th1 = cv.cvtColor(th1, cv.COLOR_BGR2GRAY)
    contours, hierarchy = cv.findContours(th1, cv.RETR_EXTERNAL,
                                          cv.CHAIN_APPROX_NONE)
    thirst = None

    for cnt in contours:
        x, y, w, h = cv.boundingRect(cnt)
        # if h < 10 or (w / orig.shape[1]) > 0.9:
        if h < 10:
            continue

        # Cropping the text block for giving input to OCR
        text_cropped = th1[y:y + h, x:x + w]

        # Apply OCR on the cropped image
        text = pytesseract.image_to_string(text_cropped)
        thirst = re.search("Thirst for adventure:\\s\\d+\\.?\\d*", text)
        if thirst is not None:
            return thirst

    return thirst


def read_remaining(driver):
    driver.save_screenshot('curr.png')
    current_screen = cv.imread('curr.png')
    cropped = current_screen[770:828, 960:1318]
    modified = prepareImageForTavernStateTextReadout(cropped)
    ret, th1 = cv.threshold(modified, 127, 255, cv.THRESH_BINARY_INV)
    th1 = cv.cvtColor(th1, cv.COLOR_BGR2GRAY)
    contours, hierarchy = cv.findContours(th1, cv.RETR_EXTERNAL,
                                          cv.CHAIN_APPROX_NONE)
    for cnt in contours:
        x, y, w, h = cv.boundingRect(cnt)
        # if h < 10 or (w / orig.shape[1]) > 0.9:
        if h < 10:
            continue

        # Cropping the text block for giving input to OCR
        text_cropped = th1[y:y + h, x:x + w]

        # Apply OCR on the cropped image
        text = pytesseract.image_to_string(text_cropped)
        print("read_remaining_ tesseract", text)
        remaining = re.search("\\d+:\\d+", text)
        if remaining is not None:
            return True, remaining.group()

    return False, ""


def read_level(driver):
    driver.save_screenshot('curr.png')
    current_screen = cv.imread('curr.png')
    cropped = current_screen[30:978, 460:1798]
    modified = prepareImageForTavernStateTextReadout(cropped)
    ret, th1 = cv.threshold(modified, 127, 255, cv.THRESH_BINARY_INV)
    th1 = cv.cvtColor(th1, cv.COLOR_BGR2GRAY)
    contours, hierarchy = cv.findContours(th1, cv.RETR_EXTERNAL,
                                          cv.CHAIN_APPROX_NONE)
    level = None

    for cnt in contours:
        x, y, w, h = cv.boundingRect(cnt)
        # if h < 10 or (w / orig.shape[1]) > 0.9:
        if h < 10:
            continue

        # Cropping the text block for giving input to OCR
        text_cropped = th1[y:y + h, x:x + w]

        # Apply OCR on the cropped image
        text = pytesseract.image_to_string(text_cropped)
        print("read level", text)
        level = re.search("you have reached level", text)
        if level is not None:
            print("level found")
            return True

    return False


def read_quest(driver, ref_quest_val):
    driver.save_screenshot('curr.png')
    current_screen = cv.imread('curr.png')
    cropped = current_screen[600:650, 820:1498]
    modified = prepareImageForQuestTextReadout(cropped)
    ret, th1 = cv.threshold(modified, 127, 255, cv.THRESH_BINARY_INV)
    th1 = cv.cvtColor(th1, cv.COLOR_BGR2GRAY)
    contours, hierarchy = cv.findContours(th1, cv.RETR_EXTERNAL,
                                          cv.CHAIN_APPROX_NONE)
    ep_per_sec = None

    for cnt in contours:
        x, y, w, h = cv.boundingRect(cnt)
        # if h < 10 or (w / orig.shape[1]) > 0.9:
        if h < 10:
            continue

        # Cropping the text block for giving input to OCR
        text_cropped = th1[y:y + h, x:x + w]

        # Apply OCR on the cropped image
        text = pytesseract.image_to_string(text_cropped)
        ep_per_sec = re.sub("[^\\d.:\\s]", "", text)
        ep_per_sec = ep_per_sec.strip()
        ep_per_sec = re.sub("\\s{2,}", " ", ep_per_sec)
        if ep_per_sec is not None:
            print(ep_per_sec)
            splitted = ep_per_sec.split(" ")
            if len(splitted) == 2:
                ep = float(splitted[0])
                time_val = splitted[1]
                time_split = time_val.split(":")
                time_in_sec = (float(time_split[0]) * 60) + float(time_split[1])
                ep_per_sec = float(ep / time_in_sec)
                if ep_per_sec > ref_quest_val * 6:
                    ep = ep[1:]
                    print("new ep: ", ep)
                    ep_per_sec = float(ep / time_in_sec)
                return ep_per_sec, time_in_sec

    return 0.0, 0


def is_quest_running():
    return

def read_ref_quest_val():
    f = open("value_ref.txt", "r")
    val = float(f.read())
    print("current value ref: ", val)
    f.close()
    return val

def write_ref_quest_val(ref_val):
    f = open("value_ref.txt", "w")
    f.write(str(ref_val))
    f.close()


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    pytesseract.pytesseract.tesseract_cmd = 'C:\\Tesseract-OCR\\tesseract.exe'
    driver = webdriver.Firefox()
    driver.implicitly_wait(15)
    # template screenshots taken with this window size
    driver.set_window_rect(0, 0, 1920, 1080)

    load_game(driver)

    while True:
        ActionChains(driver)\
            .key_down('C').pause(.2).key_up('C').pause(.2) \
            .key_down(Keys.ESCAPE).pause(.2).key_up(Keys.ESCAPE).pause(.2)\
            .key_down('C').pause(.2).key_up('C').pause(.2) \
            .key_down('T').pause(.2).key_up('T').pause(1).perform()
        thirst = read_thirst_for_adv(driver)
        if thirst is not None:
            thirst_string = thirst.group().strip()
            alu = float(re.search("\\d+\\.?\\d*", thirst_string).group())
            print("Alu remaining: ", alu)
            if (alu > 0):
                # print(alu)
                ref_quest_val = read_ref_quest_val()
                clicks_to_quest = 1
                ActionChains(driver).key_down(Keys.RETURN).pause(.2).key_up(Keys.RETURN).pause(1).perform()
                max_quest = read_quest(driver, ref_quest_val)
                print("q1: ", max_quest)

                ActionChains(driver).key_down(Keys.ARROW_RIGHT).pause(.2).key_up(Keys.ARROW_RIGHT).pause(1).perform()
                q2 = read_quest(driver, ref_quest_val)
                print("q2: ", q2)
                if q2[0] > max_quest[0]:
                    max_quest = q2
                    clicks_to_quest = 2
                elif q2[0] == max_quest[0] and q2[1] < max_quest[1]:
                    max_quest = q2
                    clicks_to_quest = 2

                ActionChains(driver).key_down(Keys.ARROW_RIGHT).pause(.2).key_up(Keys.ARROW_RIGHT).pause(1).perform()
                q3 = read_quest(driver, ref_quest_val)
                print("q3: ", q3)
                if q3[0] > max_quest[0]:
                    max_quest = q3
                    clicks_to_quest = 3
                elif q3[0] == max_quest[0] and q3[1] < max_quest[1]:
                    max_quest = q3
                    clicks_to_quest = 3
                print("selected: ", max_quest)
                write_ref_quest_val(max_quest[0])
                for _ in range(clicks_to_quest):
                    ActionChains(driver).key_down(Keys.ARROW_RIGHT).pause(.2).key_up(Keys.ARROW_RIGHT).perform()
                ActionChains(driver).key_down(Keys.RETURN).pause(.2).key_up(Keys.RETURN).pause(1).perform()
                # ActionChains(driver).key_down(Keys.RETURN).pause(.2).key_up(Keys.RETURN).pause(3).key_down(Keys.RETURN).pause(.2).key_up(Keys.RETURN).perform()
            else:
                print("no alu")
                driver.close()
                exit()
        else:
            remaining_result = read_remaining(driver)
            if remaining_result[0]:
                time_val = remaining_result[1]
                time_split = time_val.split(":")
                time_in_sec = (float(time_split[0]) * 60) + float(time_split[1])
                print("quest running, sleep for: ", time_in_sec)
                time.sleep(time_in_sec + 2)
                # ActionChains(driver).key_down(Keys.RETURN).pause(.2).key_up(Keys.RETURN).pause(2).perform()
            elif read_level(driver):
                ActionChains(driver).key_down(Keys.ESCAPE).pause(.2).key_up(Keys.ESCAPE).pause(1).perform()

        time.sleep(3)
    driver.close()
