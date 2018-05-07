# coding: utf-8

# 악보 정보 파싱해서 가져오기
import sys
import time
import selenium
import os
import shutil
import urllib
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select


# 단계마다 쉬는 시간(초단위)
pauseTime = 2
# 검색어
searchingKeyword = "검색어"
# Chromedriver 위치
chromeDriverPath = "/Users/sung/Downloads/chromedriver"
# 최초 접근 사이트 URL
site = "http://maria.catholic.or.kr/sungga/search/sungga_search.asp"
# 최종적으로 파일이 이동될 폴더 위치 설정
finalFolder = "/Users/sung/Downloads/goodnews"


# 새로이 오픈된 팝업 윈도우 handle 객체 반환
def getPopupWindowHandle(windowHandles):
    popupWindowHandle = None

    for handle in driver.window_handles:
        if handle not in windowHandles:
            popupWindowHandle = handle
            break

    return popupWindowHandle


def getScores():
    # 현재 메인 윈도우 저장해두기
    mainWindowHandle = driver.current_window_handle

    # 화면에 존재하는 악보 목록 가져오기
    listScores = driver.find_elements_by_xpath("""//*[@id="container"]/div[2]/form/table/tbody/tr""")

    # 게시물 하나하나 Command + 엔터키로 접근해서 새 창으로 띄워서 내부에 있는 악보 파일 다운로드
    for score in listScores:
        # 곡 번호, 곡 명, 혼성 악보 링크 가져오기
        scoreNumber = score.find_element_by_xpath("""td[1]/a""").text
        scoreName = score.find_element_by_xpath("""td[2]/a/spa/span""").text
        scoreLink = score.find_element_by_xpath("""td[6]/a/img""")
            
        # 혼성 악보 파일 새창에서 보기
        scoreLink.click()
        # 다운로드하는데 시간이 좀 걸리는 것 같아서 대기시간 3배로 증가
        time.sleep(pauseTime)

        # 새로운창 윈도우핸들 가져오기
        popupWindowHandle = getPopupWindowHandle(mainWindowHandle)
        # 서브 프레임 윈도우핸들에 제대로된 값이 존재한다면
        if popupWindowHandle is not None:
            # 서브 프레임으로 창 변경
            driver.switch_to.window(popupWindowHandle)

        # 다운로드 경로 존재 확인해서 없으면 생성
        if not os.path.exists(finalFolder):
            os.mkdir(finalFolder)
            
        # 이미지 파일 다운로드
        imgSrc = driver.find_element_by_xpath("""/html/body/table/tbody/tr/td/a/img""").get_attribute("src")
        scoreNewFilePathName = os.path.join(finalFolder, scoreNumber + " " + scoreName + ".jpg")
        urllib.request.urlretrieve(imgSrc, scoreNewFilePathName)
        
        # 메인 윈도우 빼고 열린거 다 닫기
        for windowHandle in driver.window_handles:
            if windowHandle != mainWindowHandle:
                driver.switch_to.window(windowHandle)
                driver.close()

        # 메인윈도우로 전환
        driver.switch_to.window(mainWindowHandle)

        # 테스트 시에는 한 페이지당 데이터 1개만 가져오기 위해 반복문 바로 탈출
        # break


# 크롬드라이버 옵션 설정(다운로드 경로 설정)
options = selenium.webdriver.ChromeOptions()
prefs = {'download.default_directory' : tempFolder}
options.add_experimental_option('prefs', prefs)


# 크롬드라이버 오픈
driver = selenium.webdriver.Chrome(chromeDriverPath, chrome_options = options)
time.sleep(pauseTime)


# 게시판 접근
driver.get(site)
time.sleep(pauseTime)


# 처음에 하단페이징 목록 한번에 가져오고 하나씩 접근
listPaging = driver.find_elements_by_xpath("""//*[@id="container"]/div[2]/form/div[2]/span/a""")
lenListPaging = len(listPaging)

# 페이징 링크가 10개면 다음 페이징이 더 있는 것이므로 계속 수행
while True:
    for i in range(lenListPaging):
        # 페이징 리스트 refreshing
        listPaging = driver.find_elements_by_xpath("""//*[@id="container"]/div[2]/form/div[2]/span/a""")

        # 다음 페이징 a tag
        nextPage = listPaging[i]
        # 다음 페이징 링크 클릭
        nextPage.click()
        time.sleep(pauseTime)

        # 악보 정보 가져오기
        getScores()
        
    # 페이징 링크 개수가 10개 미만이면 그 다음 페이지 링크가 무의미한 것 이므로 반복문 탈출
    if len(listPaging) < 10:
        break
    # 그게 아닐 경우 앞으로 데이터가 더 있다고 가정하고(사실 아닐수도 있지만) 다음 페이지 목록 가져오기
    else:
        driver.find_element_by_xpath("""//*[@id="container"]/div[2]/form/div[2]/a[3]""").click()
        
    




