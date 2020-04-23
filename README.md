# Basic usage

Add the following to your installed apps:

```
'mjml',
'wagtailbirdsong',
'wagtail.contrib.modeladmin',
```

Make a new app eg `email` and create a file called `models.py` with the following:

```
from django.db import models

from wagtail.admin.edit_handlers import FieldPanel, StreamFieldPanel
from wagtail.core.fields import StreamField

from wagtailbirdsong.blocks import DefaultBlocks
from wagtailbirdsong.models import BaseContact, Campaign


class Contact(BaseContact):
    first_name = models.CharField(max_length=255)


class SaleEmail(Campaign):
    body = StreamField(DefaultBlocks())

    panels = Campaign.panels + [
        StreamFieldPanel('body'),
    ]

    def get_contact_model(self):
        return Contact
```

In your `wagtail_hooks.py` add something like:

```
from wagtail.contrib.modeladmin.options import ModelAdmin, modeladmin_register
from wagtailbirdsong.options import EmailAdmin

from .models import Contact, SaleEmail


@modeladmin_register
class SaleEmailAdmin(EmailAdmin):
    model = SaleEmail
    menu_label = 'SaleEmail'
    menu_icon = 'pilcrow'
    menu_order = 200

@modeladmin_register
class ContactAdmin(ModelAdmin):
    model = Contact
    menu_label = 'Contacts'
    menu_icon = 'pilcrow'
    menu_order = 200

```

Create your email template in `{app_folder}/templates/{app_name}/mail/{model_name}.html` eg `email/templates/email/mail/sale_email.html`:

```
{% extends "wagtailbirdsong/mail/base_email.html" %}

{% block email_body %}
<mj-section>
    <mj-column>
        <mj-text>Hello world! {{ self.subject }}</mj-text>
        {% for b in self.body %}
            {{ b }}
        {% endfor %}
    </mj-column>
</mj-section>
{% endblock email_body %}
```

# Custom backend

Do mostly as you would in the above example, but override the `get_backend` method of the `Campaign` class. Your custom backend should follow what you see in `wagtailbirdsong.backends.BaseEmailBackend`.

For example:

```
from django.db import models

from wagtail.admin.edit_handlers import FieldPanel, StreamFieldPanel
from wagtail.core.fields import StreamField

from wagtailbirdsong.blocks import DefaultBlocks
from wagtailbirdsong.models import Campaign

from .backends import CustomBackend


class SaleEmail(Campaign):
    body = StreamField(DefaultBlocks())

    panels = Campaign.panels + [
        StreamFieldPanel('body'),
    ]

    def get_backend(self):
        return CustomBackend
```