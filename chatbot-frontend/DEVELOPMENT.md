# Development Guide

## Development Workflow

### Starting Development

1. Install dependencies:
```bash
npm install
```

2. Start the development server:
```bash
npm run dev
```

The server will start on `http://localhost:5173` (or the next available port). Hot Module Replacement (HMR) is enabled for instant updates.

### Code Organization

#### Components
- Place reusable UI components in `src/components/common/`
- Place chat-specific components in `src/components/chat/`
- Place layout components in `src/components/layout/`
- Always export components through `index.ts` for clean imports

#### State Management
- Use the `useChatStore` hook for global chat state
- Keep component-local state in individual components
- Consider adding Context API for theme/user preferences

#### Styling
- Use Tailwind utility classes for styling
- Keep responsive design in mind (mobile-first approach)
- Use `dark:` prefix for dark mode variants
- Custom animations are defined in `tailwind.config.js`

### Best Practices

#### TypeScript
- Always define proper types for props and state
- Use `type` imports for type-only imports (`import type { ... }`)
- Avoid using `any` - use `unknown` if type is truly unknown
- Keep types in `src/types/` directory

#### React
- Use functional components with hooks
- Memoize expensive computations with `useMemo`
- Memoize callbacks with `useCallback` when needed
- Use proper dependency arrays in hooks

#### Performance
- Lazy load routes and heavy components
- Optimize images and assets
- Use production build for performance testing
- Monitor bundle size with `npm run build`

### Adding New Features

#### Adding a New Component

1. Create component file in appropriate directory:
```typescript
// src/components/common/NewComponent.tsx
import type { ComponentProps } from './types';

export const NewComponent = ({ prop1, prop2 }: ComponentProps) => {
  return (
    <div className="...">
      {/* Component content */}
    </div>
  );
};
```

2. Export from index file:
```typescript
// src/components/common/index.ts
export { NewComponent } from './NewComponent';
```

3. Use in other components:
```typescript
import { NewComponent } from '@/components/common';
```

#### Adding a New API Endpoint

1. Update types in `src/types/index.ts`:
```typescript
export interface NewDataType {
  id: string;
  // ... other fields
}
```

2. Add method to API service:
```typescript
// src/services/api.ts
export const apiService = {
  // ... existing methods
  
  async getNewData(): Promise<NewDataType[]> {
    await delay(300);
    // Mock implementation
    return mockData;
  },
};
```

3. Use in components or hooks

### Testing Locally

#### Manual Testing Checklist

- [ ] Create a new conversation
- [ ] Send messages and verify responses
- [ ] Switch between conversations
- [ ] Delete a conversation
- [ ] Test on mobile viewport (use browser dev tools)
- [ ] Test dark mode (system preference)
- [ ] Test with slow network (throttle in dev tools)
- [ ] Test loading states
- [ ] Test error states (modify API to throw errors)
- [ ] Test empty states (no conversations)

#### Browser Testing

Test in multiple browsers:
- Chrome/Edge (Chromium)
- Firefox
- Safari (if on macOS)

### Debugging

#### React DevTools
Install React DevTools browser extension for debugging React components and state.

#### Console Logging
Use descriptive console logs during development:
```typescript
console.log('[ChatStore] Message sent:', message);
```

Remove or comment out before committing to production.

#### Network Debugging
Use browser Network tab to inspect API calls and responses.

### Code Quality

#### Before Committing

1. Check for TypeScript errors:
```bash
npm run build
```

2. Format code (if prettier is configured):
```bash
npm run format
```

3. Review your changes:
```bash
git diff
```

#### Commit Messages

Follow conventional commit format:
- `feat: add message editing feature`
- `fix: resolve sidebar scroll issue`
- `refactor: simplify message list logic`
- `docs: update README with deployment guide`
- `style: improve button hover states`

### Common Issues

#### Port Already in Use

If port 5173 is in use, Vite will automatically use the next available port.

#### TypeScript Errors

- Clear the TypeScript cache: Delete `tsconfig.tsbuildinfo`
- Restart your IDE/editor
- Run `npm run build` to see all errors

#### Styling Not Applied

- Restart the dev server
- Check if class names are correct
- Verify Tailwind configuration

#### HMR Not Working

- Check browser console for errors
- Restart the dev server
- Clear browser cache

### Environment Setup

#### VS Code Extensions (Recommended)

- ESLint
- Prettier
- Tailwind CSS IntelliSense
- TypeScript Importer
- Auto Rename Tag

#### IDE Settings

VS Code settings for this project:
```json
{
  "editor.formatOnSave": true,
  "editor.defaultFormatter": "esbenp.prettier-vscode",
  "editor.codeActionsOnSave": {
    "source.fixAll.eslint": true
  }
}
```

## Deployment

### Production Build

1. Build the project:
```bash
npm run build
```

2. Preview locally:
```bash
npm run preview
```

3. Deploy the `dist` folder to your hosting service

### Environment Variables

Create `.env.production` for production environment:
```
VITE_API_URL=https://api.yourproject.com
```

### Deployment Platforms

#### Vercel
```bash
npm install -g vercel
vercel
```

#### Netlify
```bash
npm install -g netlify-cli
netlify deploy --prod
```

#### AWS S3 + CloudFront
Upload the `dist` folder to S3 and configure CloudFront distribution.

#### Docker
Create a `Dockerfile`:
```dockerfile
FROM nginx:alpine
COPY dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

Build and run:
```bash
docker build -t chatbot-frontend .
docker run -p 80:80 chatbot-frontend
```

## Performance Optimization

### Code Splitting

Use dynamic imports for route-level code splitting:
```typescript
const AdminPanel = lazy(() => import('./components/AdminPanel'));
```

### Image Optimization

- Use WebP format for images
- Implement lazy loading for images
- Use appropriate sizes for different viewports

### Bundle Analysis

Analyze bundle size:
```bash
npm install -g vite-bundle-visualizer
vite-bundle-visualizer
```

### Caching Strategy

Configure cache headers in your hosting platform:
- HTML: no-cache
- JS/CSS: 1 year with content hash
- Images: 1 year

## Monitoring

### Production Monitoring

Consider integrating:
- Sentry for error tracking
- Google Analytics for usage tracking
- LogRocket for session replay
- Lighthouse CI for performance monitoring

### Performance Metrics

Monitor these key metrics:
- First Contentful Paint (FCP)
- Largest Contentful Paint (LCP)
- Time to Interactive (TTI)
- Cumulative Layout Shift (CLS)

## Maintenance

### Keeping Dependencies Updated

Check for updates:
```bash
npm outdated
```

Update dependencies:
```bash
npm update
```

Update to latest versions (be careful):
```bash
npx npm-check-updates -u
npm install
```

### Security

Run security audit:
```bash
npm audit
```

Fix vulnerabilities:
```bash
npm audit fix
```

---

Happy coding! 🚀
