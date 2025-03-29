from modeltranslation.translator import register, TranslationOptions
from .models import User, ServiceProvider, ServiceType, Product, ProductCategory

@register(User)
class UserTranslationOptions(TranslationOptions):
    fields = ('first_name', 'last_name')

@register(ServiceProvider)
class ServiceProviderTranslationOptions(TranslationOptions):
    fields = ('name', 'certifications', 'cancellation_policy')

@register(ServiceType)
class ServiceTypeTranslationOptions(TranslationOptions):
    fields = ('name', 'description')

@register(Product)
class ProductTranslationOptions(TranslationOptions):
    fields = ('name', 'description')

@register(ProductCategory)
class ProductCategoryTranslationOptions(TranslationOptions):
    fields = ('name', 'description')