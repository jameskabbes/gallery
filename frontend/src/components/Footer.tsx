import React, { useEffect } from 'react';

function Footer(): JSX.Element {
  useEffect(() => {
    let lastScrollTop = 0;
    const footer = document.getElementById('mobile-footer');

    const onScroll = () => {
      const scrollTop = window.scrollY || document.documentElement.scrollTop;

      if (scrollTop > lastScrollTop) {
        // Scrolling down
        footer?.classList.add('translate-y-full');
      } else {
        // Scrolling up
        footer?.classList.remove('translate-y-full');
      }

      lastScrollTop = scrollTop <= 0 ? 0 : scrollTop; // For Mobile or negative scrolling
    };

    window.addEventListener('scroll', onScroll);

    return () => {
      window.removeEventListener('scroll', onScroll);
    };
  }, []);

  return (
    <footer id="mobile-footer">
      <div className="bg-color h-full">This is the footer content</div>
    </footer>
  );
}

export { Footer };
