# Sportsbook Logos

This directory is used to store local sportsbook logo files. The system will automatically fall back to generated SVG logos if files are not found here.

## Supported Formats
- PNG files (recommended)
- JPG files
- SVG files

## Naming Convention
Logo files should be named using the lowercase sportsbook name:
- `fanduel.png`
- `draftkings.png`
- `betmgm.png`
- `caesars.png`
- etc.

## Fallback System
The logo loading follows this priority order:
1. **External URLs** - Predefined URLs for major sportsbooks
2. **Local Files** - Files stored in this directory
3. **Generated SVG** - Automatically generated logos with sportsbook initials

## Adding New Logos
To add a new sportsbook logo:
1. Save the logo file in this directory with the correct naming convention
2. The system will automatically detect and use it
3. Recommended size: 32x32 pixels or larger (will be scaled to fit)