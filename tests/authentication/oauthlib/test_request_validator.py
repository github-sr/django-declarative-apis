import unittest

import django.test
import mock

from django_declarative_apis import models
from django_declarative_apis.authentication.oauthlib import request_validator

from tests import testutils


class DjangoRequestValidatorTestCase(django.test.TestCase):
    def setUp(self):
        self.consumer = models.OauthConsumer.objects.create(name='test')
        self.consumer.save()

    def test_get_client_secret_with_rsa_public_key_pem(self):
        self.consumer.rsa_public_key_pem = 'something non-null'

        request = django.test.RequestFactory().get('/')

        validator = request_validator.DjangoRequestValidator(request)
        validator.consumer = self.consumer
        self.assertIsNone(validator.get_client_secret(self.consumer.key, request))

    @mock.patch('django_declarative_apis.authentication.oauthlib.request_validator.logging')
    def test_get_rsa_key(self, mock_log):
        request = django.test.RequestFactory().get('/')

        validator = request_validator.DjangoRequestValidator(request)

        self.assertEqual(validator.get_rsa_key(self.consumer.key, request), '')
        mock_log.error.assert_called_with('This should never happen, since consumer is already validated')

        validator.consumer = self.consumer
        self.consumer.rsa_public_key_pem = 'something non-null'

        self.assertEqual(
            validator.get_rsa_key(self.consumer.key, request),
            self.consumer.rsa_public_key_pem
        )