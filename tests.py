import pytest
import serializator
import re
import json


class TestTechnical():
    @pytest.mark.parametrize("insertParameters, expectedResult", [
        ({"ff": "4343"}, str),
        ({"aa": 45}, str),
        ({"mm": True}, str)
    ])
    def testReturnTypeStrAlways(self,insertParameters, expectedResult):
        methodResult = serializator.SerializeMeThis(insertParameters)
        assert type(methodResult) == expectedResult

    def testCheckItCanBeDecoded(self,goodOrder1Data):
        methodResult = serializator.SerializeMeThis(goodOrder1Data)
        DecodedDict = json.loads(methodResult)
        assert type(DecodedDict) == dict

    def testCheckContainEntities(self,goodOrder1Data):
        methodResult = serializator.SerializeMeThis(goodOrder1Data)
        DecodedDict = json.loads(methodResult)
        assert "customer" in DecodedDict and "payment" in DecodedDict and "goods" in DecodedDict

    def testSerializationNotDamageEntities(self,goodOrder1Data):
        methodResult = serializator.SerializeMeThis(goodOrder1Data)
        DecodedDict = json.loads(methodResult)

        customerIsOK = DecodedDict["customer"]==goodOrder1Data["customer"]
        paymentIsOK = DecodedDict["payment"] == goodOrder1Data["payment"]
        goodsIsOK = DecodedDict["goods"] == goodOrder1Data["goods"]
        assert customerIsOK and paymentIsOK and goodsIsOK

    def testSerializationHandleNotOneGood(self,goodOrder1Data):
        newGoods = {"goods": [
            {
                "id": 123,
                "storageId": 432,
                "sellerName": "GoodsGoodShop",
                "price": "3400"
            },
            {
                "id": 0,
                "storageId": 0,
                "sellerName": "123",
                "price": 9999999999999
            }
        ]}
        goodOrder1Data["goods"] = newGoods["goods"]
        methodResult = serializator.SerializeMeThis(goodOrder1Data)
        DecodedDict = json.loads(methodResult)
        assert DecodedDict["goods"] == newGoods["goods"]

    @pytest.mark.TypeOnly
    def testTypeCustomerFieldsOK(self,goodOrder1Data):
        methodResult = serializator.SerializeMeThis(goodOrder1Data)
        DecodedDict = json.loads(methodResult)
        customerAddress = type(DecodedDict["customer"]["Address"]) == str
        customerName = type(DecodedDict["customer"]["Name"]) == str
        assert customerAddress and customerName

    @pytest.mark.TypeOnly
    def testTypePaymentFieldsOK(self, goodOrder1Data):
        methodResult = serializator.SerializeMeThis(goodOrder1Data)
        DecodedDict = json.loads(methodResult)
        paymentType = type(DecodedDict["payment"]["paymentType"]) == str
        paymentDone = type(DecodedDict["payment"]["done"]) == bool
        paymentDataCard = type(DecodedDict["payment"]["paymentData"].split("/")[0]) == str
        paymentDataTime = type(DecodedDict["payment"]["paymentData"].split("/")[1]) == str
        assert paymentType and paymentDone and paymentDataCard and paymentDataTime

    @pytest.mark.TypeOnly
    def testTypeGoodsFieldsOK(self,goodOrder1Data):
        methodResult = serializator.SerializeMeThis(goodOrder1Data)
        DecodedDict = json.loads(methodResult)

        goodsIDType = True
        goodsStorageIdType = True
        goodsSsellerNameType = True
        goodsSpriceType = True

        for each in range(len(DecodedDict["goods"])):
            goodsID = type(DecodedDict["goods"][each]["id"]) == int
            goodsStorageId = type(DecodedDict["goods"][each]["storageId"]) == int
            goodsSsellerName = type(DecodedDict["goods"][each]["sellerName"]) == str
            goodsSprice = type(DecodedDict["goods"][each]["price"]) == int

            goodsIDType = False if goodsID == False else goodsIDType
            goodsStorageIdType = False if goodsStorageId == False else goodsStorageIdType
            goodsSsellerNameType = False if goodsSsellerName == False else goodsSsellerNameType
            goodsSpriceType = False if goodsSprice == False else goodsSpriceType
        assert goodsIDType and goodsStorageIdType and goodsSsellerNameType and goodsSpriceType


    def testNameFieldStringIsNotTooLong(self, goodOrder1Data):
        methodResult = serializator.SerializeMeThis(goodOrder1Data)
        DecodedDict = json.loads(methodResult)
        customerName = DecodedDict["customer"]["Name"]
        assert len(customerName)<120

    def testNameFieldStringIsOnlyLatin(self, goodOrder1Data):
        methodResult = serializator.SerializeMeThis(goodOrder1Data)
        DecodedDict = json.loads(methodResult)
        customerName = DecodedDict["customer"]["Name"]
        assert not bool(re.search('[а-яА-Я]', customerName))

    def testNameFieldStringNotContainForbiddenSymbols(self, goodOrder1Data):
        methodResult = serializator.SerializeMeThis(goodOrder1Data)
        DecodedDict = json.loads(methodResult)
        customerName = DecodedDict["customer"]["Name"]
        CheckResult = True
        for i in customerName:
            if i in '''@/*#!$%^?\[]-_)+=;`~.,<>'"|''':
                CheckResult = False
        assert CheckResult


# Многие проверки требуют базу данных или апи, что ради практики не оправданно. Опишу их текстом
# Авторизован ли пользователь
# существует ли вообще такой пользователь
# Проверка наличия Адреса с использованием API OSM/2GIS

class TestPayment():
    # проверка, был ли платеж запросом в банк по реквезитам платежа
    # принимает ли конкретный продавец систему оплаты
    def testPayMethodOK(self, goodOrder1Data):
        methodResult = serializator.SerializeMeThis(goodOrder1Data)
        DecodedDict = json.loads(methodResult)
        paymentType = DecodedDict["payment"]["paymentType"]
        if paymentType == "Mir" or paymentType == "Visa" or paymentType == "Master Card":
            assert True
        else:
            assert False




class TestGoodsList():
    # Есть ли несуществуюшие продавцы в списке покупок
    def testAllSellersExist(self, goodOrder1Data):
        methodResult = serializator.SerializeMeThis(goodOrder1Data)
        DecodedDict = json.loads(methodResult)
        DB = ["GoodsGoodShop", "123"]
        ListOfNotExistentSellers = []

        for each in range(len(DecodedDict["goods"])):
            goodsSsellerName = DecodedDict["goods"][each]["sellerName"]
            if goodsSsellerName not in DB:
                ListOfNotExistentSellers.append(goodsSsellerName)
        if len(ListOfNotExistentSellers)>0:
            assert False
    # Проверка на то, что товары реальны, существуют и их продажа ещё актуальна
    # проверка достаточности товаров на складе
    # цена товара не ниже уровня безубыточности
    # суммарная масса товара не выше границы
    # проверка верности подсчета скидки.






# pip install pytest-xdist
# pytest -n 3

# pytest tests.py
#py.test -m TypeOnly tests.py # для проверки только этих тестов




