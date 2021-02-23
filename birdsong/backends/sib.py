import logging
import re

from django.conf import settings
from django.contrib import messages

from django.db import close_old_connections, transaction
from django.template.loader import render_to_string
from django.utils import timezone

from birdsong.models import Campaign, CampaignStatus, Contact
from birdsong.utils import send_mass_html_mail

from datetime import datetime, timedelta

import requests

from django.core.mail.backends.base import BaseEmailBackend

import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException

logger = logging.getLogger(__name__)

class SendCampaign():
    def __init__(self, request, campaign_pk, url, payload, headers):
        super().__init__()
        self.campaign_pk = campaign_pk
        self.url = url
        self.payload = payload
        self.headers = headers
        self.request = request

    def run(self):
        try:
            response = requests.request("POST", self.url, json=self.payload, headers=self.headers)

            if response.status_code >= 300:
                status = CampaignStatus.UNSENT
                messages.error(self.request, f"Campaign failed: '{response.status_code}' '{response.text}'")
            else:
                status = CampaignStatus.SENT

            with transaction.atomic():
                Campaign.objects.filter(pk=self.campaign_pk).update(
                    status=status,
                    sent_date=timezone.now(),
                )

        except:
            logger.exception(f"Problem sending campaign(exception): {self.campaign_pk}")
            messages.error(self.request, f"Campaign failed(exception): '{self.campaign_pk}'")
        finally:
            close_old_connections()


class SIBEmailBackend(BaseEmailBackend):

    def send_email(self, request, campaign, subject, contacts):
        raise NotImplementedError

    @property
    def from_email(self):
        if hasattr(settings, 'BIRDSONG_FROM_EMAIL'):
            return settings.BIRDSONG_FROM_EMAIL
        return settings.DEFAULT_FROM_EMAIL

    @property
    def reply_to(self):
        return getattr(settings, 'BIRDSONG_REPLY_TO', self.from_email)

    def send_messages(messages):
        logging.info("SIBEmailBackend")

    def send_campaign(self, request, campaign, contacts, test_send=False):

        sib_api_key = getattr(settings, "SENDINBLUE_API_KEY", None)
        config = None
        if sib_api_key:
            config = sib_api_v3_sdk.Configuration()
            config.api_key['api-key'] = sib_api_key
        else:
            logging.info("No SIB mailing list")

        if test_send and config:
            for contact in contacts:
                content = render_to_string(
                    campaign.get_template(request),
                    campaign.get_context(request, contact),
                )
                # create an instance of the API class
                api_instance = sib_api_v3_sdk.TransactionalEmailsApi(sib_api_v3_sdk.ApiClient(config))
                send_smtp_email_sender = sib_api_v3_sdk.SendSmtpEmailSender(email=self.from_email)
                send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(sender=send_smtp_email_sender, to=[{'email':contact.email}], html_content=content, subject=campaign.subject, headers={"X-Mailin-custom": "custom_header_1:custom_value_1|custom_header_2:custom_value_2|custom_header_3:custom_value_3", "charset": "iso-8859-1"})

                try:
                    # Send a transactional email
                    api_response = api_instance.send_transac_email(send_smtp_email)
                except ApiException as e:
                    messages.error(request, f"Test email failed: {e}")
                    print("Exception when calling SMTPApi->send_transac_email: %s\n" % e)

        elif sib_api_key:
            # To satisfy module internals we need a dummy email address as the contact in the content
            api_instance = sib_api_v3_sdk.ContactsApi(sib_api_v3_sdk.ApiClient(config))
            lists = api_instance.get_lists(limit=50).lists
            lists = list(filter(lambda l: campaign.mailing_lists in l['name'], lists))
            contact = re.sub('\s+', '', campaign.mailing_lists) + "@climate.esa.int"

            content = render_to_string(
                campaign.get_template(request),
                campaign.get_context(request, contact)
            )

            sendTime = datetime.utcnow() + timedelta(minutes=5)
            sendTimeStr = sendTime.strftime("%Y-%m-%dT%H:%M:%S.000Z")

            selected_lists = [l['id'] for l in lists]
            url = "https://api.sendinblue.com/v3/emailCampaigns"

            payload = {
                "sender": {"email": self.from_email},
                "recipients": {"listIds": selected_lists},
                "inlineImageActivation": False,
                "sendAtBestTime": False,
                "abTesting": False,
                "ipWarmupEnable": False,
                "name": campaign.name,
                "htmlContent": content,
                "subject": campaign.subject,
                "scheduledAt": sendTimeStr
            }
            headers = {
                "Accept": "application/json",
                "Content-Type": "application/json",
                "api-key": sib_api_key
            }

            the_campaign = SendCampaign(
                request, campaign.pk, url, payload, headers)
            the_campaign.run()
