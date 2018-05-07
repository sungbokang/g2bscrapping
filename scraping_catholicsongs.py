# coding: utf-8

# 악보 정보 파싱해서 가져오기
import sys
import time
import selenium
import os
import shutil
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select


# 단계마다 쉬는 시간(초단위)
pauseTime = 2
# 검색어
searchingKeyword = "검색어"
# Chromedriver 위치
chromeDriverPath = "/Users/sung/Downloads/chromedriver"
# 최초 접근 사이트 URL
site = "http://sgg.or.kr/technote7/board.php?board=board04"
# 다운로드될 임시 폴더 위치 설정
tempFolder = "/Users/sung/Downloads/ssg/temp"
# 최종적으로 파일이 이동될 폴더 위치 설정
finalFolder = "/Users/sung/Downloads/ssg/final"


# 새로이 오픈된 팝업 윈도우 handle 객체 반환
def getPopupWindowHandle(windowHandles):
    popupWindowHandle = None

    for handle in driver.window_handles:
        if handle not in windowHandles:
            popupWindowHandle = handle
            break

    return popupWindowHandle


# 임시 폴더에 다운로드 받은 파일을 최종 경로로 이동하고 파일명 변경
def moveFileFromTempToFinal(newFileName):
    # 파일명이 . 으로 시작하지 않고 진짜 파일 목록만 추출
    files = [file for file in os.listdir(path = tempFolder) if (not file.startswith(".")) and os.path.isfile(os.path.join(tempFolder, file))]
    # 디렉토리 내에 파일이 하나만 있을거라 가정하고 작업
    for file in files:
        # 에러나지 않기 위해 최종 폴더 존재 체크해서 없으면 경로 생성
        if not os.path.exists(finalFolder):
            os.mkdir(finalFolder)

        # 최종 경로에 변경된 파일명으로 파일 이동
        shutil.move(os.path.join(tempFolder, file), os.path.join(finalFolder, newFileName))


def getScores():
    # 현재 메인 윈도우 저장해두기
    mainWindowHandle = driver.current_window_handle

    # 화면에 존재하는 게시물 목록 가져오기
    listScores = driver.find_elements_by_xpath("""//*[@id="mainIndexTable"]/tbody/tr/td[3]/a""")

    # 게시물 하나하나 Command + 엔터키로 접근해서 새 창으로 띄워서 내부에 있는 악보 파일 다운로드
    for score in listScores:
        # 악보 게시물에 특정 문구("개정 청소년성가")가 있을 때만 작업 수행
        if not score.find_element_by_tag_name("span").text.startswith("개정 청소년성가"):
            continue
            
        # 악보 게시물 새창에서 보기
        score.send_keys(Keys.COMMAND + Keys.RETURN)
        time.sleep(pauseTime)

        # 새로운창 윈도우핸들 가져오기
        popupWindowHandle = getPopupWindowHandle(mainWindowHandle)
        # 서브 프레임 윈도우핸들에 제대로된 값이 존재한다면
        if popupWindowHandle is not None:
            # 서브 프레임으로 창 변경
            driver.switch_to.window(popupWindowHandle)
        
        # 다운로드 링크 접근
        scoreDownloadLink = driver.find_element_by_xpath("""//*[@id="mainTextBodyDiv"]/table[1]/tbody/tr/td[1]/table/tbody/tr[3]/td[2]/span""")
        scoreDownloadLinkFileName = scoreDownloadLink.text
        scoreDownloadLink.click()
        time.sleep(pauseTime)
        
        # 임시 다운로드 폴더에 들어간 파일을 찾아서 이름을 변경하여 다른 지정된 폴더로 이동
        moveFileFromTempToFinal(scoreDownloadLinkFileName)

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

# 출력옵션 버튼 클릭
printOptBtn = driver.find_element_by_xpath("""//*[@id="mainIndexDiv"]/table[1]/tbody/tr/td[1]/a""")
printOptBtn.click()

# 페이지당 조회 횟수를 200개로 변경하고 화면 리프레시
iframe = driver.find_element_by_id("TnTeIwinframeid")
driver.switch_to_frame(iframe)
inputBoxPageSize = driver.find_element_by_xpath("""/html/body/form/table/tbody/tr[3]/td[2]/input""")
inputBoxPageSize.clear()
inputBoxPageSize.send_keys("200")
inputBoxPageSize.submit()
time.sleep(pauseTime)

# 처음에 하단페이징 목록 한번에 가져오고 하나씩 접근
listPaging = driver.find_elements_by_xpath("""//*[@id="mainIndexDiv"]/table[3]/tbody/tr[1]/td[2]/a""")
lenListPaging = len(listPaging)
for i in range(lenListPaging):
    # 다음 페이징 a tag
    nextPage = listPaging[i]
    # 다음 페이징 링크 클릭
    nextPage.click()
    time.sleep(pauseTime)

    # 페이징 리스트 refreshing
    listPaging = driver.find_elements_by_xpath("""//*[@id="mainIndexDiv"]/table[3]/tbody/tr[1]/td[2]/a""")
    
    # 악보 정보 가져오기
    getScores()

