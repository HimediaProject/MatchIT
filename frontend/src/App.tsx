import { useState } from 'react';
import LoginPage from './components/LoginPage';
import HomePage from './components/HomePage';
import JobListPage from './components/JobListPage';
import JobDetailPage from './components/JobDetailPage';
import JobComparePage from './components/JobComparePage';
import BootcampListPage from './components/BootcampListPage';
import BootcampDetailPage from './components/BootcampDetailPage';
import BootcampComparePage from './components/BootcampComparePage';
import ChatbotPage from './components/ChatbotPage';
import MyPage from './components/MyPage';

type PageType = 'login' | 'home' | 'jobList' | 'jobDetail' | 'jobCompare' | 'bootcampList' | 'bootcampDetail' | 'bootcampCompare' | 'chatbot' | 'myPage';

export default function App() {
  const [currentPage, setCurrentPage] = useState<PageType>('home');
  const [selectedJobs, setSelectedJobs] = useState<number[]>([]);
  const [selectedBootcamps, setSelectedBootcamps] = useState<number[]>([]);

  const renderPage = () => {
    switch (currentPage) {
      case 'login':
        return <LoginPage onNavigate={setCurrentPage} />;
      case 'home':
        return <HomePage
          onNavigate={setCurrentPage}
          onAddToCompare={(id: number, type?: 'job' | 'bootcamp') => {
          if (type === 'bootcamp') {
            setSelectedBootcamps((prev) => {
              if (prev.includes(id)) return prev;
              if (prev.length >= 3) {
                window.alert('최대 3개까지 비교할 수 있습니다.');
                return prev;
              }
              return [...prev, id];
            });
          } else {
            setSelectedJobs((prev) => {
              if (prev.includes(id)) return prev;
              if (prev.length >= 3) {
                window.alert('최대 3개까지 비교할 수 있습니다.');
                return prev;
              }
              return [...prev, id];
            });
          }
          }}
          selectedJobs={selectedJobs}
          setSelectedJobs={setSelectedJobs}
          selectedBootcamps={selectedBootcamps}
          setSelectedBootcamps={setSelectedBootcamps}
        />;
      case 'jobList':
        return (
          <JobListPage
            onNavigate={setCurrentPage}
            selectedJobs={selectedJobs}
            setSelectedJobs={setSelectedJobs}
            onAddToCompare={(id: number, type?: 'job' | 'bootcamp') => {
              // delegate to the same handler used by HomePage
              if (type === 'bootcamp') {
                if (selectedJobs.length > 0) {
                  window.alert('부트캠프와 채용공고는 섞어서 비교할 수 없습니다. 현재 채용공고가 선택되어 있습니다.');
                  return;
                }
                setSelectedBootcamps((prev) => {
                  if (prev.includes(id)) return prev;
                  if (prev.length >= 3) {
                    window.alert('최대 3개까지 비교할 수 있습니다.');
                    return prev;
                  }
                  return [...prev, id];
                });
              } else {
                if (selectedBootcamps.length > 0) {
                  window.alert('채용공고와 부트캠프는 섞어서 비교할 수 없습니다. 현재 부트캠프가 선택되어 있습니다.');
                  return;
                }
                setSelectedJobs((prev) => {
                  if (prev.includes(id)) return prev;
                  if (prev.length >= 3) {
                    window.alert('최대 3개까지 비교할 수 있습니다.');
                    return prev;
                  }
                  return [...prev, id];
                });
              }
            }}
            selectedBootcamps={selectedBootcamps}
          />
        );
      case 'jobDetail':
        return <JobDetailPage onNavigate={setCurrentPage} />;
      case 'jobCompare':
        return <JobComparePage onNavigate={setCurrentPage} selectedJobs={selectedJobs} />;
      case 'bootcampList':
        return (
          <BootcampListPage
            onNavigate={setCurrentPage}
            selectedBootcamps={selectedBootcamps}
            setSelectedBootcamps={setSelectedBootcamps}
            onAddToCompare={(id: number, type?: 'job' | 'bootcamp') => {
              if (type === 'job') {
                if (selectedBootcamps.length > 0) {
                  window.alert('채용공고와 부트캠프는 섞어서 비교할 수 없습니다. 현재 부트캠프가 선택되어 있습니다.');
                  return;
                }
                setSelectedJobs((prev) => {
                  if (prev.includes(id)) return prev;
                  if (prev.length >= 3) {
                    window.alert('최대 3개까지 비교할 수 있습니다.');
                    return prev;
                  }
                  return [...prev, id];
                });
              } else {
                if (selectedJobs.length > 0) {
                  window.alert('부트캠프와 채용공고는 섞어서 비교할 수 없습니다. 현재 채용공고가 선택되어 있습니다.');
                  return;
                }
                setSelectedBootcamps((prev) => {
                  if (prev.includes(id)) return prev;
                  if (prev.length >= 3) {
                    window.alert('최대 3개까지 비교할 수 있습니다.');
                    return prev;
                  }
                  return [...prev, id];
                });
              }
            }}
            selectedJobs={selectedJobs}
          />
        );
      case 'bootcampDetail':
        return <BootcampDetailPage onNavigate={setCurrentPage} />;
      case 'bootcampCompare':
        return (
          <BootcampComparePage onNavigate={setCurrentPage} selectedBootcamps={selectedBootcamps} />
        );
      case 'chatbot':
        return <ChatbotPage onNavigate={setCurrentPage} />;
      case 'myPage':
        return <MyPage onNavigate={setCurrentPage} />;
      default:
        return <LoginPage onNavigate={setCurrentPage} />;
    }
  };

  return (
    <div className="min-h-screen bg-gray-100">
      {/* Top Navigation - Hidden on Login */}
      {currentPage !== 'login' && (
        <header className="bg-white border-b border-gray-300">
          <div className="max-w-[1400px] mx-auto px-6 py-3 flex items-center justify-between">
            <div className="flex items-center gap-12">
              <button
                onClick={() => setCurrentPage('home')}
                className="text-xl border border-gray-900 px-4 py-1"
              >
                IT Career
              </button>
              <nav className="flex gap-8">
                <button
                  onClick={() => setCurrentPage('jobList')}
                  className="text-sm hover:underline"
                >
                  채용공고
                </button>
                <button
                  onClick={() => setCurrentPage('bootcampList')}
                  className="text-sm hover:underline"
                >
                  부트캠프
                </button>
              </nav>
            </div>
            <div className="flex items-center gap-4">
              <button
                onClick={() => setCurrentPage('myPage')}
                className="px-4 py-1 border border-gray-900 text-sm"
              >
                MY
              </button>
              <button
                onClick={() => setCurrentPage('login')}
                className="text-sm text-gray-600 hover:underline"
              >
                로그인
              </button>
            </div>
          </div>
        </header>
      )}

      {/* Page Content */}
      {renderPage()}

      {/* Floating Chatbot Button - Hidden on Login */}
      {currentPage !== 'login' && (
        <button
          onClick={() => setCurrentPage('chatbot')}
          className="fixed bottom-8 right-8 w-14 h-14 rounded-full border-2 border-gray-900 bg-white hover:bg-gray-200 flex items-center justify-center shadow-lg"
        >
          <span className="text-xl">💬</span>
        </button>
      )}
    </div>
  );
}
