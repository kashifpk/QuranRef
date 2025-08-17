# QuranRef Frontend

Modern Vue.js 3 frontend for the QuranRef application with TypeScript and Vuetify UI components.

## Tech Stack

- **Framework**: Vue.js 3 with Composition API
- **Language**: TypeScript with strict mode
- **UI Library**: Vuetify 3 (Material Design)
- **Package Manager**: Bun (ultra-fast JavaScript runtime)
- **Build Tool**: Vite for lightning-fast HMR
- **State Management**: Pinia
- **Routing**: Vue Router 4
- **HTTP Client**: Mande
- **Utilities**: VueUse for reactive utilities

## Project Structure

```
frontend/
├── src/
│   ├── components/        # Vue components
│   │   ├── AppHeaderComponent.vue
│   │   ├── HomePageComponent.vue
│   │   ├── SearchPageComponent.vue
│   │   └── SurahPageComponent.vue
│   ├── QuranRefMainApp.vue    # Main app component
│   ├── main.ts            # Application entry point
│   ├── router.ts          # Vue Router configuration
│   ├── store.ts           # Pinia store
│   ├── type_defs.ts       # TypeScript interfaces
│   └── utils.ts           # Utility functions
├── public/                # Static assets
├── .env                   # Environment variables
├── package.json           # Dependencies (Bun-compatible)
├── bun.lockb              # Bun lock file
├── tsconfig.json          # TypeScript configuration
├── tsconfig.app.json      # App-specific TS config
├── vite.config.ts         # Vite configuration
└── index.html             # Entry HTML file
```

## Development Setup

### Docker Development (Recommended)

```bash
# From project root - start all services
./dev-docker.sh up

# Frontend auto-starts with hot-reload
# Edit files in src/ and see changes instantly at http://localhost:41149

# Run commands inside the container:
docker exec quranref_frontend_dev bun run build    # Production build
docker exec quranref_frontend_dev vue-tsc -b       # Type checking
docker exec quranref_frontend_dev bun test         # Run tests
```

The frontend will be available at http://localhost:41149 with hot module replacement (HMR).

### Direct Host Development

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies with Bun
bun install

# Start development server with HMR
bun run dev

# The app will be available at http://localhost:5173
```

## Available Scripts

```bash
# Development server with hot-reload
bun run dev

# Production build
bun run build

# Preview production build locally
bun run preview

# Type checking
bun run type-check

# Build with type checking
bun run build-only

# Linting (if configured)
bun run lint

# Format code (if configured)
bun run format
```

## Environment Variables

Create a `.env` file in the frontend directory:

```env
# Static assets URL
STATIC_URL=/

# API configuration
VITE_API_BASE_URL=http://localhost:41148/api/v1  # Docker development
# VITE_API_BASE_URL=http://localhost:8000/api/v1   # Direct host development

# Website base URL
VITE_WEBSITE_BASE_URL=http://localhost:41149      # Docker development
# VITE_WEBSITE_BASE_URL=http://localhost:5173      # Direct host development
```

## Key Components

### Main Application (`QuranRefMainApp.vue`)
- Application shell with navigation drawer
- Vuetify theme configuration
- Responsive layout management

### Router (`router.ts`)
- Client-side routing with Vue Router 4
- Routes:
  - `/` - Home page with Surah list
  - `/search` - Search interface
  - `/surah/:id` - Individual Surah view
  - `/404` - Not found page

### Store (`store.ts`)
- Pinia store for global state management
- Handles:
  - Surah list caching
  - Search results
  - API communication
  - Loading states

### API Integration
- Uses Mande for HTTP requests
- Endpoints consumed:
  - `GET /surahs` - Fetch all Surahs
  - `GET /text/{surah}/{languages}` - Get Surah text
  - `GET /search/{term}/{lang}/{translations}` - Search
  - `GET /words-by-letter/{letter}` - Browse words
  - `GET /ayas-by-word/{word}/{languages}` - Get verses by word

## UI Components

### Vuetify Configuration
- Material Design 3 components
- Custom theme with Islamic color palette
- Responsive breakpoints
- RTL support for Arabic text

### Component Architecture
- Uses Vue 3 Composition API with `<script setup>`
- TypeScript for type safety
- Props validation with TypeScript interfaces
- Reactive state with `ref` and `reactive`
- Computed properties for derived state

## Building for Production

```bash
# Using Docker
docker exec quranref_frontend_dev bun run build

# Or directly with Bun
bun run build

# Output will be in dist/ directory
# Optimized, minified, and tree-shaken
```

The build process:
1. Compiles TypeScript to JavaScript
2. Bundles all modules with Vite
3. Optimizes images and assets
4. Generates source maps
5. Creates production-ready files in `dist/`

## Performance Optimizations

- **Code Splitting**: Automatic route-based splitting
- **Lazy Loading**: Components loaded on demand
- **Asset Optimization**: Images and fonts optimized
- **Tree Shaking**: Unused code eliminated
- **Compression**: Gzip/Brotli support ready
- **Caching**: Proper cache headers configuration

## Development Tips

### Hot Module Replacement (HMR)
- Instant updates without page refresh
- Preserves component state during updates
- Works for styles, templates, and scripts

### TypeScript Support
```typescript
// Use proper typing for better IDE support
import type { Surah, Aya } from './type_defs'

// Typed props
defineProps<{
  surah: Surah
  ayas: Aya[]
}>()
```

### Vuetify Components
```vue
<v-app>
  <v-navigation-drawer v-model="drawer">
    <!-- Navigation content -->
  </v-navigation-drawer>
  
  <v-main>
    <v-container>
      <!-- Main content -->
    </v-container>
  </v-main>
</v-app>
```

## Troubleshooting

### Port Already in Use
- Docker development uses port 41149
- Direct host uses port 5173
- Change with: `bun run dev --port 3000`

### API Connection Issues
- Verify backend is running
- Check VITE_API_BASE_URL in `.env`
- For Docker: use http://localhost:41148
- For host: use http://localhost:8000

### Build Errors
- Clear cache: `rm -rf node_modules .vite`
- Reinstall: `bun install`
- Check TypeScript errors: `bun run type-check`

### HMR Not Working
- Check file watchers limit on Linux
- Restart dev server
- Clear browser cache

## Dependencies Management

Using Bun for package management:

```bash
# Add dependency
bun add package-name

# Add dev dependency
bun add -d package-name

# Update all dependencies
bun update

# Remove dependency
bun remove package-name

# Check outdated packages
bunx npm-check-updates
```

## Testing

```bash
# Run unit tests (when configured)
bun test

# Run with coverage
bun test --coverage

# Watch mode
bun test --watch
```

## Code Style

- Follow Vue.js style guide
- Use Composition API with `<script setup>`
- Prefer TypeScript interfaces over types
- Use Vuetify components consistently
- Keep components small and focused
- Extract reusable logic to composables