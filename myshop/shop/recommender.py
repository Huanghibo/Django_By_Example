import redis
from django.conf import settings
from .models import Product

r = redis.StrictRedis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=settings.REDIS_DB)


class Recommender(object):
    def get_product_key(self, id):
        return 'product:{}:purchased_with'.format(id)

    def products_bought(self, products):
        product_ids = [p.id for p in products]
        # 迭代所有的产品ID两次，并且跳过相同的产品
        for product_id in product_ids:
            for with_id in product_ids:
                # 获取用户购买产品时一同购买的其他产品
                if product_id != with_id:
                    # 给get_product_key(product_id)返回的key里面的with_id值（一起付款的产品）加1分，分数指with_id与指定产品一起购买的次数
                    r.zincrby(self.get_product_key(product_id), with_id, amount=1)

    def suggest_products_for(self, products, max_results=6):
        product_ids = [p.id for p in products]
        if len(products) == 1:
            # 如果只有1个产品，就根据这个产品的ID，来从redis的以这个ID为键的值里面按分数降序取出结果
            suggestions = r.zrange(
                self.get_product_key(product_ids[0]), 0, -1, desc=True)[:max_results]
        else:
            # 如果有多个产品，就把所有的id合并为一个字符串，以tmp_字符串为临时键
            flat_ids = ''.join([str(id) for id in product_ids])
            tmp_key = 'tmp_{}'.format(flat_ids)
            # 把当前的多个产品的有序集的评分的并集相加作为值，保存在redis
            # zunionstore方法对所给键的求和，然后在新的键中保存分数的求和
            keys = [self.get_product_key(id) for id in product_ids]
            r.zunionstore(tmp_key, keys)
            # 从临时键的值中删除当前的多个产品的id
            r.zrem(tmp_key, *product_ids)
            # 按照分数降序取出临时键里面的结果
            suggestions = r.zrange(tmp_key, 0, -1, desc=True)[:max_results]
            # 删除临时键
            r.delete(tmp_key)
            # 把从取出的结果的id生成列表
        suggested_products_ids = [int(id) for id in suggestions]
        # 根据上面的ID组成的列表查询出product对象，并组成列表
        suggested_products = list(Product.objects.filter(id__in=suggested_products_ids))
        # 把对象列表按照id字段在id列表中的索引位置升序排序
        suggested_products.sort(key=lambda x: suggested_products_ids.index(x.id))
        return suggested_products

    # 清除所有的推荐
    def clear_purchases(self):
        # values_list方法根据id字段查询出结果，组成元祖
        for id in Product.objects.values_list('id', flat=True):
            r.delete(self.get_product_key(id))
