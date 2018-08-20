from decimal import Decimal
from django.conf import settings
from shop.models import Product
from coupons.models import Coupon


# session中间件使当前session在request对象中可用，使用request.seesion连接当前session，使用方式和Python字典相似，会话字典接收任何默认的可被序列化为JSON的Python对象
# 当用户登录时他们的匿名session将会丢失，然后将会为认证后的用户创建新的session，如果想在登录后依然需要在匿名session中储存的数据，需要从旧的session中复制数据到新的session
# Django默认使用django.contrib.sessions的Sessions模型把session保存在数据库中，还有其他选择：
    # Database sessions（数据库session）:session数据将会被保存在数据库中。这是默认的session引擎。
    # File-based sessions（基于文件的session）：session数据保存在文件系统中。
    # Cached sessions（缓存session）：session数据储存于缓存后端。你可以使用  CACHES 设置来制定一个缓存后端。在缓存系统中储存session数据会有更好的性能表现。
    # Cached database sessions（缓存于数据库中的session）：session数据保存于可高速写入的缓存和数据库中。只会在缓存中没有数据时才会从数据库中读取数据。
    # Cookie-based sessions（基于cookie的session）：session数据储存于发送向浏览器的 cookie 中。
    # 为了得到更好的性能，建议使用基于缓存的session引擎，Django支持Mercached、Redis等第三方缓存后端和其他的缓存系统。
# 有几个配置项，最重要的部分是SESSION_ENGINE，其他设置如下：
    # SESSION_COOKIE_AGE ：cookie保持的时间，以秒为单位，默认值为1209600（2周）
    # SESSION_COOKIE_DOMAIN ：cookie使用的域名，把它的值设置为.mydomain.com来使跨域名cookie生效
    # SESSION_COOKIE_SECURE ：布尔值，意思是只有在连接为HTTPS 时cookie才会被发送
    # SESSION_EXPIRE_AT_BROWSER_CLOSE ：布尔值，意思是会话会在浏览器关闭时就过期，SESSION_EXPIRE_AT_BROWSER_CLOSE可以选择使用browser-length或者持久会话，默认的设置是False，强制把会话的有效期设置为SESSION_COOKIE_AGE的值。
    # 如果SESSION_EXPIRE_AT_BROWSER_CLOSE的值为True，会话将会在用户关闭浏览器时过期，且SESSION_COOKIE_AGE将不会对此有任何影响，可以使用request.session的set_expiry()方法来覆写当前会话的有效期
    # SESSION_SAVE_EVERY_REQUEST ：布尔值，如果为True，每次请求的session都将会被储存进数据库中，session过期时间也会每次刷新
class Cart(object):
    def __init__(self, request):
        """    初始化购物车    """
        # 当需要购物车时，检查顾客是否已经设置session key，如果会话中没有购物车，就创建新的购物车，然后把它保存在购物车的session key中
        self.session = request.session
        cart = self.session.get(settings.CART_SESSION_ID)
        self.coupon_id = self.session.get('coupon_id')
        if not cart:
            # 使用空字典是因为希望购物车字典使用产品ID作为键，以数量和单价为值，且能保证同样的产品在购物车中不被重复添加
            cart = self.session[settings.CART_SESSION_ID] = {}
        self.cart = cart

    # 对于连续的请求，检查顾客是否已经设置session key，并获取购物车内的物品和他们的Product对象
    # 添加产品或者更新产品的数量
    def add(self, product, quantity=1, update_quantity=False):
        product_id = str(product.id)
        # 如果购物车session中没有这个产品
        if product_id not in self.cart:
            self.cart[product_id] = {'quantity': 0, 'price': str(product.price)}
        # 如果update_quantity=True，按照给定的数量参数更新
        if update_quantity:
            self.cart[product_id]['quantity'] = quantity
        # 如果update_quantity=False，已存在的数量+新的数量
        else:
            self.cart[product_id]['quantity'] += quantity
        self.save()

    def save(self):
        # 把购物车所有的改动保存到session中
        self.session[settings.CART_SESSION_ID] = self.cart
        # 标记session为"modified"，告诉Django session已经被改动，需要将它保存起来
        self.session.modified = True

    def remove(self, product):
        # 从购物车删除产品
        product_id = str(product.id)
        if product_id in self.cart:
            del self.cart[product_id]
            self.save()

    # 迭代购物车当中的物品，然后获取相应的Product实例，并添加到购物车
    def __iter__(self):
        # 更新购物车字典里的产品ID的product键的值是相应的Product实例
        product_ids = self.cart.keys()
        products = Product.objects.filter(id__in=product_ids)
        for product in products:
            self.cart[str(product.id)]['product'] = product
        # 更新购物车字典里的产品的价格为数字而非字符串，并更新总价
        for item in self.cart.values():
            item['price'] = Decimal(item['price'])
            item['total_price'] = item['price'] * item['quantity']
            yield item

    # 计算购物车中所有物品的数量
    def __len__(self):
        return sum(item['quantity'] for item in self.cart.values())

    # 计算购物车中所有物品的总价
    def get_total_price(self):
        return sum(Decimal(item['price']) * item['quantity'] for item in self.cart.values())

    # 从session清空购物车
    def clear(self):
        del self.session[settings.CART_SESSION_ID]
        self.session.modified = True

    # 方法变为属性
    @property
    def coupon(self):
        # 如果session中有优惠码
        if self.coupon_id:
            return Coupon.objects.get(id=self.coupon_id)
        return None

    def get_discount(self):
        if self.coupon:
            # 上面的coupon属性(方法)，返回的是Coupon对象，含有discount属性
            return (self.coupon.discount / Decimal('100')) * self.get_total_price()
        return Decimal('0')

    def get_total_price_after_discount(self):
        return self.get_total_price() - self.get_discount()
