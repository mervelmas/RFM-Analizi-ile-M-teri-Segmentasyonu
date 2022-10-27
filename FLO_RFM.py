PROJE GÖREVLERİ

#Adım1: flo_data_20K.csv verisini okuyunuz.Dataframe’in kopyasını oluşturunuz.

import datetime as dt
import pandas as pd
pd.set_option('display.max_columns', None)
pd.set_option('display.float_format', lambda x: '%.3f' % x)
df_ = pd.read_csv("C:\\Users\\Merve.Elmas\\Desktop\\datasets\\flo_data_20k.csv")
df = df_.copy()

#Adım2: Veri setinde
#a. İlk 10 gözlem,
#b. Değişken isimleri,
#c. Betimsel istatistik,
#d. Boş değer,
#e. Değişken tipleri, incelemesi yapınız.

df.head(10)
df.columns
df.describe().T
df.isnull().sum()
df.dtypes


#Adım3: Omnichannel müşterilerin hem online'dan hemde offline platformlardan alışveriş yaptığını ifade etmektedir. Her bir müşterinin toplam
#alışveriş sayısı ve harcaması için yeni değişkenler oluşturunuz.

df['total_of_purchase'] = df["order_num_total_ever_online"] + df["order_num_total_ever_offline"]
df['total_of_spending'] = df["customer_value_total_ever_online"] + df["customer_value_total_ever_offline"]
df.head()

#Adım4: Değişken tiplerini inceleyiniz. Tarih ifade eden değişkenlerin tipini date'e çeviriniz.

#2.yol
df['first_order_date'] = pd.to_datetime(df['first_order_date'])
df['last_order_date '] = pd.to_datetime(df['last_order_date'])
df['last_order_date_online'] = pd.to_datetime(df['last_order_date_online'])
df['last_order_date_offline '] = pd.to_datetime(df['last_order_date_offline'])

df.dtypes
#Adım5: Alışveriş kanallarındaki müşteri sayısının, toplam alınan ürün sayısının ve toplam harcamaların dağılımına bakınız.

df.groupby("order_channel").agg({"master_id": ["count"],
                                 "total_of_purchase": ["sum"],
                                 "total_of_spending": ["sum"]}).head()

#Adım6: En fazla kazancı getiren ilk 10 müşteriyi sıralayınız.

df.sort_values("total_of_spending", ascending=False)[:10]


#Adım7: En fazla siparişi veren ilk 10 müşteriyi sıralayınız.

df.groupby(["master_id"].agg({"total_of_purchase" : "sum"}).sort_values("total_of_purchase", ascending=False).head(10)

#Adım8: Veri ön hazırlık sürecini fonksiyonlaştırınız.

def datafunc(df, csv=False):
    df['total_of_purchase'] = df["order_num_total_ever_online"] + df["order_num_total_ever_offline"]
    df['total_of_spending'] = df["customer_value_total_ever_online"] + df["customer_value_total_ever_offline"]
    date_convert = ["first_order_date", "last_order_date", "last_order_date_online", "last_order_date_offline"]
    df[date_convert] = df[date_convert].apply(pd.to_datetime)

    return df

datafunc(df).head()

#Görev 2: RFM Metriklerinin Hesaplanması
#Adım 1: Recency, Frequency ve Monetary tanımlarını yapınız.

df["last_order_date"].max()
today_date = dt.datetime(2021,6,1)
type(today_date)
df.head()

#Recency : "last_order_date" : lambda last_order_date: (today_date - last_order_date.max()).days
#Frequency : "total_of_purchase : lambda total_of_purchase: total_of_purchase.nunique()
#Monetary : "total_of_spending" : lambda total_of_spending: total_of_spending.sum()

#Adım 2: Müşteri özelinde Recency, Frequency ve Monetary metriklerini hesaplayınız.

rfm = df.groupby('master_id').agg({'last_order_date': lambda last_order_date: (today_date - last_order_date.max()).days,
                                   'total_of_purchase': lambda total_of_purchase: total_of_purchase.sum(),
                                   'total_of_spending': lambda total_of_spending: total_of_spending.sum()})
rfm.head()

#Adım 3: Hesapladığınız metrikleri rfm isimli bir değişkene atayınız.
#Adım 4: Oluşturduğunuz metriklerin isimlerini recency, frequency ve monetary olarak değiştiriniz.

rfm.columns = ["recency","frequency","monetary"]

rfm.describe().T

#Görev 3: RF Skorunun Hesaplanması
#Adım 1: Recency, Frequency ve Monetary metriklerini qcut yardımı ile 1-5 arasında skorlara çeviriniz.
#Adım 2: Bu skorları recency_score, frequency_score ve monetary_score olarak kaydediniz.
#Adım 3: recency_score ve frequency_score’u tek bir değişken olarak ifade ediniz ve RF_SCORE olarak kaydediniz.

rfm["recency_score"] = pd.qcut(rfm['recency'], 5, labels = [5,4,3,2,1])
rfm["frequency_score"] = pd.qcut(rfm['frequency'].rank(method="first"), 5, labels = [1,2,3,4,5])
rfm["monetary_score"]= pd.qcut(rfm['monetary'], 5, labels= [1,2,3,4,5])

rfm["RFM_SCORE"] = (rfm['recency_score'].astype(str) +
                    rfm['frequency_score'].astype(str))

rfm.head()
rfm.describe().T

rfm[rfm["RFM_SCORE"] == "55"]
rfm[rfm["RFM_SCORE"] == "11"]

#Görev 4: RF Skorunun Segment Olarak Tanımlanması
#Adım 1: Oluşturulan RF skorları için segment tanımlamaları yapınız.
#Adım 2: Aşağıdaki seg_map yardımı ile skorları segmentlere çeviriniz.

seg_map = {
    r'[1-2][1-2]': 'hibernating',
    r'[1-2][3-4]': 'at_risk',
    r'[1-2]5': 'cant_loose',
    r'3[1-2]': 'about_to_sleep',
    r'33': 'need_attention',
    r'[3-4][4-5]': 'loyal_customers',
    r'41': 'promising',
    r'51': 'new_customers',
    r'[4-5][2-3]': 'potential_loyalists',
    r'5[4-5]': 'champions'
}

rfm['segment'] = rfm['RFM_SCORE'].replace(seg_map, regex=True)
rfm = rfm[["recency", "frequency", "monetary", "segment"]]

#Görev 5: Aksiyon Zamanı !
#Adım1: Segmentlerin recency, frequnecy ve monetary ortalamalarını inceleyiniz.

rfm[["segment","recency","frequency","monetary"]].groupby("segment").agg(["mean"])

#Adım2: RFM analizi yardımıyla aşağıda verilen 2 case için ilgili profildeki müşterileri bulun ve müşteri id'lerini csv olarak kaydediniz.
#a. FLO bünyesine yeni bir kadın ayakkabı markası dahil ediyor. Dahil ettiği markanın ürün fiyatları genel müşteri
#tercihlerinin üstünde. Bu nedenle markanın tanıtımı ve ürün satışları için ilgilenecek profildeki müşterilerle özel olarak
#iletişime geçmek isteniliyor. Sadık müşterilerinden(champions, loyal_customers) ve kadın kategorisinden alışveriş
#yapan kişiler özel olarak iletişim kurulacak müşteriler. Bu müşterilerin id numaralarını csv dosyasına kaydediniz.

segment_A= rfm[(rfm["segment"] == "champions") | (rfm["segment"] == "loyal_customers")]
segment_A.shape[0]

segment_B = df[(df["interested_in_categories_12"]).str.contains("KADIN")]
segment_B.shape[0]

case_one = pd.merge(segment_A,segment_B[["interested_in_categories_12", "master_id"]],on=["master_id"])
case_one.columns

case_one = case_one.drop(case_one.loc[:,'recency':'interested_in_categories_12'].columns,axis=1)

case_one.to_csv("one_case_customer_info_1.csv")


#b. Erkek ve Çocuk ürünlerinde %40'a yakın indirim planlanmaktadır. Bu indirimle ilgili kategorilerle ilgilenen geçmişte
#iyi müşteri olan ama uzun süredir alışveriş yapmayan kaybedilmemesi gereken müşteriler, uykuda olanlar ve yeni
#gelen müşteriler özel olarak hedef alınmak isteniyor. Uygun profildeki müşterilerin id'lerini csv dosyasına kaydediniz.

segment_C = rfm[(rfm["segment"] == "about_to_sleep") | (rfm["segment"] == "new_customers")]
segment_C.shape[0]

segment_D = df[(df["interested_in_categories_12"]).str.contains("ERKEK|COCUK")]
segment_D.shape[0]

case_second = pd.merge(segment_C,segment_D[["interested_in_categories_12", "master_id"]],on=["master_id"])

case_second = case_second.drop(case_second.loc[:,'recency':'interested_in_categories_12'].columns,axis=1)

case_second.to_csv("second_case_customer_info_2.csv")
