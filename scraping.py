# 조달청 나라장터 정보 파싱하기

import sys
import time
import selenium
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select

# 단계마다 쉬는 시간(초단위)
pauseTime = 2
# 검색어
searchingKeyword = "검색어"
# Chromedriver 위치
chromeDriverPath = "~/Downloads/chromedriver"


def ignoreJsAlert():
	try:
		alert = driver.switch_to_alert()
		alert.accept()
		time.sleep(pauseTime)
	except:
		print("no javascript alert open")


def getPopupWindowHandle(mainWindowHandle):
	popupWindowHandle = None

	for handle in driver.window_handles:
		if handle != mainWindowHandle:
			popupWindowHandle = handle
			break

	return popupWindowHandle


def getFactoryInfo():
	# 현재 메인 윈도우 저장해두기
	mainWindowHandle = driver.current_window_handle

	# 화면에 존재하는 공장소재지 목록 가져오기
	listFactory = driver.find_elements_by_xpath("""//*[@id="prdLstFrm"]/table/tbody/tr/td[3]/ul/li[11]/a""")

	# 공장정보들을 담아둘 list
	infoList = list()

	for factory in listFactory:
		factory.click()
		time.sleep(pauseTime)

		# 서브프레임 윈도우핸들 가져오기
		popupWindowHandle = getPopupWindowHandle(mainWindowHandle)
		# 서브 프레임 윈도우핸들에 제대로된 값이 존재한다면
		if popupWindowHandle is not None:
			# 서브 프레임으로 창 변경
			driver.switch_to.window(popupWindowHandle)

		# 잠깐 쉬기(창간 전환)
		time.sleep(pauseTime)

		# 서비 프레임 내의 iframe(id = "bizrnoInfoFrame") 접근
		bizrnoInfoFrame = driver.find_element_by_id("bizrnoInfoFrame")
		driver.switch_to_frame(bizrnoInfoFrame)

		# 공장 정보 추가
		popupInfo = getPopupInfo()
		infoList.append(popupInfo)

		# 현재 창 닫기
		driver.switch_to.window(popupWindowHandle)
		driver.close()
		# 메인윈도우로 전환
		driver.switch_to.window(mainWindowHandle)
		driver.switch_to.frame("sub")

		# 테스트 시에는 한 페이지당 데이터 1개만 가져오기
		# if len(infoList) > 0:
		# 	break

	return infoList


def getPopupInfo():
	popupInfo = list()

	# 상호명, 사업자등록번호, 대표자명, 본사주소, 본사전화번호, 팩스번호, 종업원수, 홈페지
	basicInfoList = driver.find_elements_by_xpath("""//*[@id="container"]/div[2]/table/tbody/tr/td""")
	for basicInfo in basicInfoList:
		popupInfo.append(basicInfo.text)

	# 공장명, 우편번호, 주소, 전화번호, 팩스번호
	popupInfo.append(driver.find_element_by_xpath("""//*[@id="container"]/div[4]/table/tbody/tr[2]/td[2]""").text)
	popupInfo.append(driver.find_element_by_xpath("""//*[@id="container"]/div[4]/table/tbody/tr[2]/td[3]""").text)
	popupInfo.append(driver.find_element_by_xpath("""//*[@id="container"]/div[4]/table/tbody/tr[2]/td[4]""").text)
	popupInfo.append(driver.find_element_by_xpath("""//*[@id="container"]/div[4]/table/tbody/tr[3]/td[1]""").text)
	popupInfo.append(driver.find_element_by_xpath("""//*[@id="container"]/div[4]/table/tbody/tr[3]/td[2]""").text)

	# 담당자명, 부서명, 전화번호, 팩스번호
	popupInfo.append(driver.find_element_by_xpath("""//*[@id="container"]/div[6]/table/tbody/tr/td[2]""").text)
	popupInfo.append(driver.find_element_by_xpath("""//*[@id="container"]/div[6]/table/tbody/tr/td[3]""").text)
	popupInfo.append(driver.find_element_by_xpath("""//*[@id="container"]/div[6]/table/tbody/tr/td[4]""").text)
	popupInfo.append(driver.find_element_by_xpath("""//*[@id="container"]/div[6]/table/tbody/tr/td[5]""").text)

	return tuple(popupInfo)


# 크롬드라이버 오픈
driver = selenium.webdriver.Chrome(chromeDriverPath)

# 나라장터 홈페이지 접근
driver.get("http://shopping.g2b.go.kr")

# 검색창에 체육시설탄성포장재 검색어 넣고 조회
driver.switch_to_frame("sub")
elem = driver.find_element_by_id("kwd")
elem.send_keys("체육시설탄성포장재")
elem.send_keys(Keys.RETURN)
time.sleep(pauseTime)

# 전체목록조회 링크 접속
elem2 = driver.find_element_by_xpath('''//*[@id="m_contents"]/div[2]/div[4]/div[2]/h3/a[1]''')
elem2.click()
time.sleep(pauseTime)
# 액티브엑스 플러그인 뜨면 그냥 씹기
ignoreJsAlert()

# 페이지당 조회 횟수를 100개로 변경하고 화면 리프레시
selectPageSizeChkBox = Select(driver.find_element_by_id("pageSizeChkBox"))
selectPageSizeChkBox.select_by_value("100")
listRfsBtn = driver.find_element_by_xpath("""//*[@id="SrchGoodsLstForm"]/div[5]/div/div[2]/span[3]/a""")
listRfsBtn.click()
time.sleep(pauseTime)

# 액티브엑스 플러그인 뜨면 그냥 씹기
ignoreJsAlert()

# 공장소재지 정보 담을 리스트 생성
factoryInfoSet = set()

# 공장소재지 하나씩 클릭하여 가져온 정보 합치기
factoryInfoSet.update(getFactoryInfo())

# 처음에 하단페이징 목록 한번에 가져오고 하나씩 접근
listPaging = driver.find_elements_by_xpath("""//*[@id="m_contents"]/div[2]/div[2]/span/span/a""")
lenListPaging = len(listPaging)
for i in range(lenListPaging):
	# 다음 페이징 a tag
	nextPage = listPaging[i]
	# 다음 페이징 링크 클릭
	nextPage.click()
	time.sleep(pauseTime)
	# 액티브엑스 플러그인 뜨면 그냥 씹기
	ignoreJsAlert()

	# 공장소재지 하나씩 클릭하여 가져온 정보 합치기
	factoryInfoSet.update(getFactoryInfo())

	# 페이징 리스트 refreshing
	listPaging = driver.find_elements_by_xpath("""//*[@id="m_contents"]/div[2]/div[2]/span/span/a""")

# 가져온 데이터를 파일로 출력했다 나중에 윈도우PC에서 엑셀import 처리
f = open("./Desktop/scraping.txt", "w", encoding = "utf-8")
try:
	while True:
		factoryInfo = factoryInfoSet.pop()
		for item in factoryInfo:
			print(item, end = "|", file = f)
		print("", file = f)
except:
	print("Done")
f.close()

"""
# 메인화면에서의 리스트 접근
//*[@id="prdLstFrm"]/table/tbody[1]/tr/td[3]/ul/li[11]/a
//*[@id="prdLstFrm"]/table/tbody[2]/tr/td[3]/ul/li[11]/a
//*[@id="prdLstFrm"]/table/tbody[10]/tr/td[3]/ul/li[11]/a

# 메인화면에서 각 리스트의 주요 항목
원산지
주요부품1[원산지]
주요부품2[원산지]
핵심부품[원산지]
//*[@id="prdLstFrm"]/table/tbody[1]/tr/td[3]/ul/li[6]
//*[@id="prdLstFrm"]/table/tbody[1]/tr/td[3]/ul/li[7]
//*[@id="prdLstFrm"]/table/tbody[1]/tr/td[3]/ul/li[8]
//*[@id="prdLstFrm"]/table/tbody[1]/tr/td[3]/ul/li[9]

# 팝업창의 정보의 기본 목록
상호명
사업자등록번호
대표자명
본사주소
본사전화번호
팩스번호
종업원수
홈페지
//*[@id="container"]/div[2]/table/tbody/tr[1]/td
//*[@id="container"]/div[2]/table/tbody/tr[2]/td
//*[@id="container"]/div[2]/table/tbody/tr[8]/td

#공장정보1
공장명
우편번호
주소
전화번호
팩스번호
//*[@id="container"]/div[4]/table/tbody/tr[2]/td[2]
//*[@id="container"]/div[4]/table/tbody/tr[2]/td[3]
//*[@id="container"]/div[4]/table/tbody/tr[2]/td[4]
//*[@id="container"]/div[4]/table/tbody/tr[3]/td[1]
//*[@id="container"]/div[4]/table/tbody/tr[3]/td[2]

# 담당자정보1
담당자명
부서명
전화번호
팩스번호
//*[@id="container"]/div[6]/table/tbody/tr/td[2]
//*[@id="container"]/div[6]/table/tbody/tr/td[3]
//*[@id="container"]/div[6]/table/tbody/tr/td[4]
//*[@id="container"]/div[6]/table/tbody/tr/td[5]

# Paging 구조
1
//*[@id="m_contents"]/div[2]/div[2]/span/strong/span
//*[@id="m_contents"]/div[2]/div[2]/span/span[1]/a
//*[@id="m_contents"]/div[2]/div[2]/span/span[2]/a
//*[@id="m_contents"]/div[2]/div[2]/span/span[3]/a

2
//*[@id="m_contents"]/div[2]/div[2]/span/span[1]/a
//*[@id="m_contents"]/div[2]/div[2]/span/strong
//*[@id="m_contents"]/div[2]/div[2]/span/span[2]/a
//*[@id="m_contents"]/div[2]/div[2]/span/span[3]/a

3
//*[@id="m_contents"]/div[2]/div[2]/span/span[1]/a
//*[@id="m_contents"]/div[2]/div[2]/span/span[2]/a
//*[@id="m_contents"]/div[2]/div[2]/span/strong
//*[@id="m_contents"]/div[2]/div[2]/span/span[3]/a
"""
