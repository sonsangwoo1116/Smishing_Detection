import { useState } from 'react';

const MAX_LENGTH = 2000;

const SAMPLE_MESSAGES = [
  // === 고위험 (HIGH) ===
  {
    label: '🔴 CJ대한통운 사칭',
    message: '[CJ대한통운] 고객님 택배가 주소지 불일치로 배송 불가합니다. 주소 재확인 후 재배송 신청해주세요.\nhttps://cjlogis-kr.top/delivery/check?id=849271635',
    sender: '1588-1255',
  },
  {
    label: '🔴 국민건강보험',
    message: '[국민건강보험공단] 귀하의 건강검진 결과 이상소견이 발견되었습니다. 정밀검사 예약 및 결과 확인:\nhttps://nhis-checkup.xyz/result/2026/view',
    sender: '1577-1000',
  },
  {
    label: '🔴 교통범칙금',
    message: '[경찰청교통민원24] 미납 교통범칙금(128,000원)이 있습니다. 기한 내 미납 시 가산금이 부과됩니다. 납부확인:\nhttp://efine-police.click/pay/62819',
    sender: '182',
  },
  {
    label: '🔴 카드 해외결제',
    message: '[KB국민카드] 해외승인 USD 892.40 (아마존) 본인 결제가 아닌 경우 즉시 신고해주세요.\n고객센터 연결: https://bit.ly/kb-fraud-center',
    sender: '1588-1688',
  },
  {
    label: '🔴 법원 출석요구',
    message: '[서울중앙지방법원] 귀하에 대한 소송이 접수되었습니다. 사건번호 2026가합12345. 전자소송 서류 확인:\nhttps://ecourt-go-kr.xyz/case/view?no=202612345',
    sender: '02-530-1114',
  },
  {
    label: '🔴 앱 설치 유도',
    message: '[우리은행] 고객님의 계좌가 비정상 거래로 감지되었습니다. 보안앱을 설치하여 본인인증을 완료해주세요.\nhttp://wooribank-sec.top/app/install.apk',
    sender: '1588-5000',
  },
  // === 위험 (WARNING) ===
  {
    label: '🟡 가족 사칭',
    message: '엄마 나 핸드폰 떨어뜨려서 화면이 안 보여ㅠㅠ 수리 맡겼는데 임시폰이라 전화가 안돼. 급한 건데 문화상품권 5만원짜리 2장만 사서 핀번호 사진 찍어서 보내줄 수 있어?',
    sender: '010-3847-9912',
  },
  {
    label: '🟡 택배 부재중',
    message: '[로젠택배] 부재중으로 택배 보관중입니다. 금일 내 미수령시 반송처리됩니다.\n수령 일정 변경: https://han.gl/a8Kv2',
    sender: '1588-9988',
  },
  {
    label: '🟡 정부지원금',
    message: '[정부24] 2026년 하반기 긴급생활안정지원금 대상자로 선정되셨습니다. 아래 링크에서 신청하세요.\nhttps://gov24-support.xyz/apply',
    sender: '1588-2188',
  },
  {
    label: '🟡 부고 사칭',
    message: '부고 알려드립니다. 故 김OO님(향년 78세)께서 별세하셨습니다. 발인: 4/9(수) 오전 7시 서울성모병원 장례식장.\n부의금 및 조화 안내: https://me2.do/x7Rp3qW',
    sender: '010-2716-0043',
  },
  // === 정상 (NORMAL) ===
  {
    label: '🟢 정상 택배',
    message: '[CJ대한통운] 배송완료: 경비실 앞 보관 (송장번호 649184720153) 배송기사: 김민수 (010-1234-5678)',
    sender: '1588-1255',
  },
  {
    label: '🟢 정상 카드',
    message: '[KB국민카드] 1월15일 12:30 이디야커피 5,200원 일시불 결제완료. 잔여한도: 4,283,000원',
    sender: '1588-1688',
  },
  {
    label: '🟢 회사 업무',
    message: '안녕하세요 개발팀 상우님, 내일 오후 2시에 스미싱 탐지 프로젝트 중간 리뷰 미팅이 있습니다. 5층 회의실B에서 뵙겠습니다.',
    sender: '',
  },
];

export default function MessageInput({ onAnalyze, loading }) {
  const [message, setMessage] = useState('');
  const [sender, setSender] = useState('');

  const charCount = message.length;
  const isOverLimit = charCount > MAX_LENGTH;
  const canSubmit = message.trim().length > 0 && !isOverLimit && !loading;

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!canSubmit) return;
    onAnalyze(message, sender);
  };

  const handleSample = (sample) => {
    setMessage(sample.message);
    setSender(sample.sender);
  };

  return (
    <form onSubmit={handleSubmit} className="card space-y-4">
      <div>
        <label htmlFor="message-input" className="block text-sm font-medium text-gray-300 mb-2">
          분석할 문자 메시지
        </label>
        <textarea
          id="message-input"
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          placeholder="의심되는 문자 메시지를 붙여넣으세요..."
          rows={4}
          className="input-field resize-y min-h-[100px]"
          disabled={loading}
        />
        <div className="flex justify-between mt-1">
          <span className="text-xs text-gray-500">
            전체 메시지를 입력하면 더 정확한 분석이 가능합니다
          </span>
          <span className={`text-xs ${isOverLimit ? 'text-red-400' : 'text-gray-500'}`}>
            {charCount}/{MAX_LENGTH}
          </span>
        </div>
      </div>

      <div>
        <label htmlFor="sender-input" className="block text-sm font-medium text-gray-300 mb-2">
          발신자 번호 <span className="text-gray-500 font-normal">(선택)</span>
        </label>
        <input
          id="sender-input"
          type="text"
          value={sender}
          onChange={(e) => setSender(e.target.value)}
          placeholder="010-0000-0000"
          className="input-field"
          disabled={loading}
        />
      </div>

      <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-3">
        <button
          type="submit"
          disabled={!canSubmit}
          className="btn-primary flex items-center justify-center gap-2"
        >
          {loading ? (
            <>
              <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin-slow" />
              분석 중...
            </>
          ) : (
            <>
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M21 21l-5.197-5.197m0 0A7.5 7.5 0 105.196 5.196a7.5 7.5 0 0010.607 10.607z" />
              </svg>
              분석하기
            </>
          )}
        </button>

        <div className="w-full mt-2">
          <span className="text-xs text-gray-500 block mb-2">테스트 예시 메시지:</span>
          <div className="flex flex-wrap gap-1.5">
            {SAMPLE_MESSAGES.map((sample) => (
              <button
                key={sample.label}
                type="button"
                onClick={() => handleSample(sample)}
                disabled={loading}
                className="text-xs px-2.5 py-1 rounded-md border border-gray-700 text-gray-400
                           hover:border-cyan-500/50 hover:text-cyan-400 transition-colors
                           disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {sample.label}
              </button>
            ))}
          </div>
        </div>
      </div>
    </form>
  );
}
