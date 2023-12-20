import React from 'react';
import { Link } from 'react-router-dom';

interface NavItem {
  label: string;
  href: string;
}

interface NavBarProps {
  items: NavItem[];
}

function NavBar(): JSX.Element {
  return NavBarTemplate({
    items: [{ label: 'Home', href: '/' }],
  });
}

function NavBarTemplate({ items }: NavBarProps): JSX.Element {
  return (
    <nav>
      <ul className="flex flex-row space-x-3">
        {items.map((item) => (
          <li key={item.href}>
            <Link
              className="text-blue-500 hover:text-blue-700 dark:text-blue-300 dark:hover:text-blue-100"
              to={item.href}
            >
              {item.label}
            </Link>
          </li>
        ))}
      </ul>
    </nav>
  );
}

export { NavBar };
