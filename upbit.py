from typing import Dict, List, Sequence, Any
from urllib.parse import urlencode, unquote
import uuid
import hashlib
import jwt
import requests


# 유틸 함수
def _get_amount_only(seq: Sequence):
    return [float(item['amount']) for item in seq]


class Upbit:
    """Upbit Wrapper"""
    _SERVER_URL = "https://api.upbit.com"

    def __init__(self, access_key, secret_key, debug=False):
        self._access_key = access_key
        self._secret_key = secret_key
        self._debug = debug
        self._verbose(f"_access_key : {self._access_key}")
        self._verbose(f"_secret_key : {self._secret_key}")

    # 메인 모듈

    def get_deposit_history(self, currency='KRW'):
        """원화 입금 기록"""
        params = {
            'currency': currency,
            'state': 'accepted',
        }
        return _get_amount_only(
            self._get_many_page('/v1/deposits', params=params))

    def get_withdraws_history(self, currency="KRW"):
        """원화 출금 기록"""
        params = {
            'currency': currency,
            'state': 'done',
        }
        return _get_amount_only(
            self._get_many_page("/v1/withdraws", params=params))

    def get_net_deposit_of_krw(self):
        """원화 순입금 기록 : 원화 입금 기록 - 원화 출금 기록"""
        return sum(self.get_deposit_history()) - sum(self.get_withdraws_history())

    # 서브 모듈

    def _verbose(self, msg):
        if self._debug:
            print(msg)

    def _get(self,
             path: str,
             params: Dict[str, Any] = None,
             ) -> requests.Response:
        """requests.get Wrapper"""
        res = requests.get(f'{Upbit._SERVER_URL}{path}',
                           params=params,
                           headers=self._generate_auth_token(params))
        self._verbose(res.status_code)
        self._verbose(res.json())
        return res

    def _get_many_page(self, path, params) -> List:
        """여러 페이지 일괄 수집"""
        result = []
        params['page'] = 1
        while True:
            self._verbose(f"PAGE {params['page']}")
            json = self._get(path, params).json()
            result += json
            if not json or (len(json) < 100):
                break
            params['page'] += 1
        self._verbose(f"RESULT : {len(result)}")
        return result

    def _generate_auth_token(self, params=None):
        """인증 토큰 헤더 생성"""
        if params is None:
            params = {}
        query_string = unquote(urlencode(params, doseq=True)).encode("utf-8")

        m = hashlib.sha512()
        m.update(query_string)
        query_hash = m.hexdigest()

        payload = {
            'access_key': self._access_key,
            'nonce': str(uuid.uuid4()),
            'query_hash': query_hash,
            'query_hash_alg': 'SHA512',
        }

        jwt_token = jwt.encode(payload, self._secret_key)
        authorization = 'Bearer {}'.format(jwt_token)
        return {
            'Authorization': authorization,
        }
