import pandas as pd
import glob
import matplotlib.pyplot as plt
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os

def generate_sales_report():
    # 1. 데이터 로드
    product_list = glob.glob("./data/*품목별*.csv")
    if not product_list:
        print("데이터 파일을 찾을 수 없습니다.")
        return

    file_path = product_list[0]
    print(f"처리 중인 파일: {file_path}")
    
    # CSV 읽기 (EUC-KR 인코딩)
    try:
        df = pd.read_csv(file_path, encoding="EUC-KR")
    except Exception as e:
        print(f"파일 읽기 오류: {e}")
        return

    # 2. 데이터 전처리 및 통계 계산
    # '품목' 컬럼을 인덱스로 설정
    df = df.set_index("품목")
    
    # 월별 매출 합계 (열 기준 합계)
    monthly_sales = df.sum(axis=0)
    
    # 품목별 매출 합계 (행 기준 합계)
    category_sales = df.sum(axis=1)
    
    print("데이터 분석 완료")

    # 3. 그래프 생성 및 저장
    # 한글 폰트 설정 (Windows)
    plt.rc('font', family='Malgun Gothic')
    plt.rc('axes', unicode_minus=False)
    
    # 그래프 저장 폴더 생성
    if not os.path.exists('output'):
        os.makedirs('output')

    # 3-1. 월별 매출 추이 (Line Plot)
    plt.figure(figsize=(10, 6))
    plt.plot(monthly_sales.index, monthly_sales.values, marker='o', linestyle='-', color='b')
    plt.title('월별 매출 추이')
    plt.xlabel('월')
    plt.ylabel('매출액')
    plt.xticks(rotation=45)
    plt.grid(True)
    plt.tight_layout()
    plt.savefig('output/monthly_trend.png')
    plt.close()

    # 3-2. 품목별 매출 비중 (Pie Chart)
    plt.figure(figsize=(8, 8))
    plt.pie(category_sales, labels=category_sales.index, autopct='%1.1f%%', startangle=140)
    plt.title('품목별 매출 비중')
    plt.axis('equal')
    plt.tight_layout()
    plt.savefig('output/category_share.png')
    plt.close()
    
    print("그래프 생성 완료")

    # 4. PDF 보고서 생성
    pdf_file = "sales_report.pdf"
    c = canvas.Canvas(pdf_file, pagesize=A4)
    width, height = A4

    # 한글 폰트 등록 (ReportLab)
    # Windows 기본 폰트 경로 사용
    font_path = "C:/Windows/Fonts/malgun.ttf"
    if os.path.exists(font_path):
        pdfmetrics.registerFont(TTFont("MalgunGothic", font_path))
        c.setFont("MalgunGothic", 24)
    else:
        print("Malgun Gothic 폰트를 찾을 수 없습니다. 기본 폰트를 사용합니다.")
        c.setFont("Helvetica", 24)

    # 제목
    c.drawString(100, height - 100, "월간 매출 보고서")
    
    c.setFont("MalgunGothic", 12) if os.path.exists(font_path) else c.setFont("Helvetica", 12)
    c.drawString(100, height - 130, f"대상 파일: {os.path.basename(file_path)}")
    
    # 요약 통계
    total_revenue = category_sales.sum()
    best_month = monthly_sales.idxmax()
    best_month_sales = monthly_sales.max()
    best_category = category_sales.idxmax()
    
    text_y = height - 160
    c.drawString(100, text_y, f"총 매출액: {total_revenue:,} 원")
    c.drawString(100, text_y - 20, f"최고 매출 월: {best_month} ({best_month_sales:,} 원)")
    c.drawString(100, text_y - 40, f"최고 매출 품목: {best_category}")

    # 그래프 삽입
    # 이미지 위치 및 크기 조정
    c.drawImage("output/monthly_trend.png", 50, height - 500, width=500, height=300)
    c.drawImage("output/category_share.png", 100, height - 800, width=400, height=300)

    c.save()
    print(f"PDF 보고서 생성 완료: {pdf_file}")

if __name__ == "__main__":
    generate_sales_report()