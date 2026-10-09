from django.db import models
import pyotp

class Client(models.Model):
    name = models.TextField("Имя")
    phone = models.CharField("Номер телефона", max_length=20)
    picture = models.ImageField("Изображение", null=True, upload_to="clients")
    user = models.ForeignKey("auth.User", verbose_name="Пользователь", on_delete=models.CASCADE, null=True)
    totp_key = models.CharField(max_length=128, null=True, blank=True, default=pyotp.random_hex)

    class Meta:
        verbose_name = "Клиент" 
        verbose_name_plural = "Клиенты"
    
    def __str__(self) -> str:
        return self.name

class Order(models.Model):
    number = models.IntegerField("номер заказа")
    client = models.ForeignKey("Client", on_delete=models.CASCADE, null=True)
    class Meta:
        verbose_name = "Заказ" 
        verbose_name_plural = "Заказы"
        
    def __str__(self) -> str:
        return str(self.number)
    
class Feedback(models.Model):
    review = models.TextField("текст отзыва")
    client = models.ForeignKey("Client", on_delete=models.CASCADE, null=True)
    class Meta:
        verbose_name = "Отзыв" 
        verbose_name_plural = "Отзывы"
        
    def __str__(self) -> str:
        return str(self.review)

class OrderComposition(models.Model):
    order = models.ForeignKey("Order", on_delete=models.CASCADE, null=True)
    bearing = models.ForeignKey("Bearing", on_delete=models.CASCADE, null=True)
    ammount = models.IntegerField("Количество")

    class Meta:
        verbose_name = "Состав заказа" 
        verbose_name_plural = "Составы заказов"

class Bearing(models.Model):
    name = models.TextField("Название")
    inner_d = models.IntegerField("Внутренний диаметр")
    outer_d = models.IntegerField("Внешний диаметр")
    height = models.IntegerField("Высота")
    price = models.IntegerField("Цена")
    ammount = models.IntegerField("Количество")
    picture = models.ImageField("Изображение", null=True, upload_to="bearings")

    class Meta:
        verbose_name = "Подшипник"
        verbose_name_plural = "Подшипники"
    
    def __str__(self) -> str:
        return self.name
