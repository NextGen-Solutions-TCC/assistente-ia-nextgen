# esse arquivo serve para olhar para o gmail do usuario que não pode ser repetido mas o user pode usar o mesmo nome com um gmail diferente

from allauth.socialaccount.adapter import DefaultSocialAccountAdapter

class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    def populate_user(self, request, sociallogin, data):
        user = super().populate_user(request, sociallogin, data)
        email = data.get('email', '')
        if email:
            user.username = email.replace('@', '_').replace('.', '_')
        return user 