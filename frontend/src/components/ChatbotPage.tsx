import { useState } from 'react';

type NavigateFunction = (page: string) => void;

interface ChatbotPageProps {
  onNavigate: NavigateFunction;
}

interface Message {
  type: 'user' | 'bot';
  content: string;
  cards?: Array<{
    type: 'job' | 'bootcamp';
    title: string;
    subtitle: string;
    info: string;
  }>;
}

export default function ChatbotPage({ onNavigate }: ChatbotPageProps) {
  const [messages] = useState<Message[]>([
    {
      type: 'user',
      content: '백엔드 개발자 취업 준비 중입니다. Python과 Django를 할 줄 알아요.',
    },
    {
      type: 'bot',
      content: '보유하신 기술 스택 기반으로 매칭률 높은 채용공고 5개를 추천합니다.',
      cards: [
        {
          type: 'job',
          title: '백엔드 개발자',
          subtitle: '테크 회사 A',
          info: '매칭 92%',
        },
        {
          type: 'job',
          title: 'Django 개발자',
          subtitle: '스타트업 B',
          info: '매칭 88%',
        },
        {
          type: 'job',
          title: 'Python 서버 개발자',
          subtitle: '기업 C',
          info: '매칭 85%',
        },
        {
          type: 'job',
          title: '주니어 백엔드',
          subtitle: '회사 D',
          info: '매칭 82%',
        },
        {
          type: 'job',
          title: 'API 개발자',
          subtitle: '테크 E',
          info: '매칭 80%',
        },
      ],
    },
    {
      type: 'bot',
      content: '경쟁력 향상을 위해 Docker와 AWS 학습을 추천합니다. 관련 교육 과정 3개를 찾았습니다.',
      cards: [
        {
          type: 'bootcamp',
          title: 'DevOps 마스터 과정',
          subtitle: '코딩 부트캠프 A',
          info: '6개월 · 국비지원',
        },
        {
          type: 'bootcamp',
          title: 'Docker & Kubernetes',
          subtitle: '테크 아카데미 B',
          info: '3개월 · 350만원',
        },
        {
          type: 'bootcamp',
          title: 'AWS 인프라 구축',
          subtitle: '온라인 스쿨 C',
          info: '2개월 · 200만원',
        },
      ],
    },
    {
      type: 'user',
      content: '첫 번째 공고 더 자세히 알려주세요',
    },
    {
      type: 'bot',
      content:
        '테크 회사 A의 백엔드 개발자 공고입니다. 경력 2년 이상, 연봉 5000-7000만원 조건이며, 상세 페이지에서 확인하실 수 있습니다.',
    },
  ]);

  const [inputValue, setInputValue] = useState('');

  return (
    <div className="max-w-[1100px] mx-auto px-6 py-8 h-[calc(100vh-80px)] flex flex-col">
      <h1 className="mb-6">AI 커리어 추천 챗봇</h1>

      {/* Chat Messages */}
      <div className="flex-1 border border-gray-400 bg-white p-6 overflow-y-auto mb-4">
        <div className="space-y-6">
          {messages.map((message, idx) => (
            <div key={idx}>
              {message.type === 'user' ? (
                <div className="flex justify-end">
                  <div className="max-w-xl border border-gray-900 bg-gray-900 text-white p-4 text-sm">
                    {message.content}
                  </div>
                </div>
              ) : (
                <div className="flex justify-start">
                  <div className="max-w-3xl">
                    <div className="border border-gray-400 bg-gray-50 p-4 mb-3 text-sm">
                      {message.content}
                    </div>

                    {message.cards && (
                      <div className="grid grid-cols-1 gap-2">
                        {message.cards.map((card, cardIdx) => (
                          <button
                            key={cardIdx}
                            onClick={() =>
                              onNavigate(card.type === 'job' ? 'jobDetail' : 'bootcampDetail')
                            }
                            className="border border-gray-400 bg-white hover:bg-gray-50 p-3 flex items-center justify-between text-left"
                          >
                            <div className="flex items-center gap-3">
                              <div className="w-10 h-10 border border-gray-500 flex items-center justify-center bg-gray-50">
                                <span className="text-xs text-gray-400">×</span>
                              </div>
                              <div>
                                <div className="text-xs text-gray-600 mb-1">[{card.subtitle}]</div>
                                <div className="text-sm">{card.title}</div>
                              </div>
                            </div>
                            <span className="px-2 py-1 border border-gray-900 text-xs">
                              {card.info}
                            </span>
                          </button>
                        ))}
                      </div>
                    )}
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Input Area */}
      <div className="border-2 border-gray-900 bg-white p-4">
        <div className="flex gap-3 mb-3">
          <input
            type="text"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            placeholder="메시지를 입력하세요..."
            className="flex-1 border border-gray-900 px-4 py-3 bg-gray-50 text-sm"
          />
          <button className="px-8 py-3 border-2 border-gray-900 bg-gray-900 text-white text-sm">
            전송
          </button>
        </div>
        <div className="flex gap-2">
          <button className="px-3 py-1 border border-gray-900 bg-white text-xs hover:bg-gray-50">
            추천 공고 보기
          </button>
          <button className="px-3 py-1 border border-gray-900 bg-white text-xs hover:bg-gray-50">
            부트캠프 추천
          </button>
          <button className="px-3 py-1 border border-gray-900 bg-white text-xs hover:bg-gray-50">
            스킬 분석
          </button>
        </div>
      </div>
    </div>
  );
}
