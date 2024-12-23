# image

**1.1 題目**

香蕉成熟度判斷

**1.2 Introduction**
	
*1.2.1 動機*

香蕉的成熟度是影響農產品品質、營養價值及市場價格的關鍵因素，透
過影像處理進行成熟度判斷提升農業產值與品質。

*1.2.2 目的或做完此專題，要解決的問題*

農業生產者在收成時容易面臨果實過早採收或過熟的問題。

**1.3 文獻探討(別人的方法，優缺點)**
	
利用CNN 模型來識別番茄的不同類別或成熟度。
優點 : 準確度高、且背景複雜也可偵測。
缺點 : 需要大量數據做訓練。
參考資料 : https://discord.com/channels/@me/1237749377066340372/1319612514715172884 

**1.4 你的方法**

1.尺寸與形狀分析 :

Canny Edge Detection 邊緣檢測偵測果實位置。

a.灰階轉換：將圖片轉換為灰階（cv2.cvtColor），減少計算複雜度。

b.調整對比和亮度：
使用 cv2.convertScaleAbs，調整對比（alpha）和亮度（beta），加強香蕉與背景的區別。

c.高斯模糊：應用高斯模糊（cv2.GaussianBlur）減少噪聲。

d.Canny 邊緣偵測：使用 cv2.Canny 偵測邊緣，設定低閾值（10）和高閾值（400），提取物體的邊界。

e.形態學操作：
使用膨脹（cv2.dilate）填補邊緣中可能的斷裂。
使用形態學閉運算（cv2.morphologyEx）進一步連接斷裂的輪廓。


2.顏色分析 : 

HSV 色空間檢測果實的顏色範圍，分三大類型: 黃色(成熟)、綠色(未熟)、黑
色(過熟)。

a.HSV 色彩轉換：將香蕉圖片轉換為 HSV 顏色空間（cv2.cvtColor），因為 
HSV 更適合進行顏色範圍的分割。
H (色相)：用於區分顏色，如黃色、綠色和棕色。
S (飽和度)：控制顏色的鮮豔程度。
V (亮度)：控制顏色的明暗。

b.定義顏色範圍：
黃色區域：lower_yellow = [15, 50, 50]，upper_yellow = [38, 255, 255]
棕色區域：lower_brown = [0, 10, 10]，upper_brown = [50, 255, 180]
綠色區域：lower_green = [35, 50, 50]，upper_green = [80, 255, 255]

c.遮罩計算：
使用 cv2.inRange 函數，根據 HSV 範圍生成遮罩，篩選出圖片中黃
色、棕色和綠色的像素。
使用 cv2.bitwise_and 將這些遮罩限制在香蕉區域內。

d.顏色比例計算：
分別計算黃色、棕色和綠色像素佔整個香蕉區域的比例。
cv2.countNonZero 用於計算遮罩中的有效像素數量。

e.成熟度分類：
根據顏色比例，判斷香蕉的成熟度：
綠色比例高 → 未熟 (Unripe)
棕色比例高 → 過熟 (Overripe)
黃色為主 → 適中成熟 (Moderately Ripe)

**1.5 實驗結果**

文字結果 : 
a.影像編號 
b.三色占比(Yellow,Brown,Green)
c.成熟度(Unripe,Moderately
 Ripe,Overripe)

影像結果 :
a.原始影像 
b.邊緣偵測
c.各顏色遮罩 

**1.6 參考資料**
https://www.kaggle.com/datasets/l3llff/banana/data
https://www.kaggle.com/code/swapnilnaique/tomato-classification/notebook
