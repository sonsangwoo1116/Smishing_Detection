const API_KEY_STORAGE = 'smishing_api_key';
const DEFAULT_API_KEY = 'sk-smish-bootstrap-test-key-001';

export function getApiKey() {
  return sessionStorage.getItem(API_KEY_STORAGE) || DEFAULT_API_KEY;
}

export function setApiKey(key) {
  if (key) {
    sessionStorage.setItem(API_KEY_STORAGE, key);
  } else {
    sessionStorage.removeItem(API_KEY_STORAGE);
  }
}

export function hasApiKey() {
  return true; // 기본 키가 항상 존재
}

function getErrorMessage(status) {
  const messages = {
    400: '잘못된 요청입니다. 메시지를 확인해주세요.',
    401: 'API Key가 유효하지 않습니다. 설정에서 키를 확인해주세요.',
    404: '해당 분석 결과를 찾을 수 없습니다.',
    422: '요청 데이터 형식이 올바르지 않습니다.',
    429: '요청이 너무 많습니다. 잠시 후 다시 시도해주세요.',
    500: '서버 오류가 발생했습니다.',
    503: '서비스가 일시적으로 이용 불가합니다.',
  };
  return messages[status] || `알 수 없는 오류가 발생했습니다. (${status})`;
}

async function apiCall(endpoint, options = {}) {
  const { signal, ...restOptions } = options;

  const headers = {
    'Content-Type': 'application/json',
    ...restOptions.headers,
  };

  const apiKey = getApiKey();
  if (apiKey) {
    headers['X-API-Key'] = apiKey;
  }

  let response;
  try {
    response = await fetch(endpoint, {
      ...restOptions,
      headers,
      signal,
    });
  } catch (err) {
    if (err.name === 'AbortError') {
      throw { status: 0, message: '요청이 취소되었습니다.', aborted: true };
    }
    throw { status: 0, message: '서버에 연결할 수 없습니다. 네트워크를 확인해주세요.' };
  }

  if (!response.ok) {
    let detail = '';
    try {
      const body = await response.json();
      detail = body.detail || body.message || '';
    } catch {
      // ignore parse errors
    }
    throw {
      status: response.status,
      message: detail || getErrorMessage(response.status),
    };
  }

  return response.json();
}

export async function analyzeMessage(message, sender, signal) {
  const body = { message };
  if (sender && sender.trim()) {
    body.sender = sender.trim();
  }
  const result = await apiCall('/api/v1/analyze', {
    method: 'POST',
    body: JSON.stringify(body),
    signal,
  });
  return result;
}

export async function getHistory({ page = 1, size = 20, riskLevel, startDate, endDate } = {}) {
  const params = new URLSearchParams();
  params.set('page', page);
  params.set('size', size);
  if (riskLevel && riskLevel !== 'ALL') {
    params.set('risk_level', riskLevel);
  }
  if (startDate) params.set('start_date', startDate);
  if (endDate) params.set('end_date', endDate);

  return apiCall(`/api/v1/history?${params.toString()}`);
}

export async function getHistoryDetail(id) {
  return apiCall(`/api/v1/history/${id}`);
}

export async function getHealth() {
  return apiCall('/api/v1/health');
}
