# Contributing to AI Call Center System

Thank you for your interest in contributing! 🎉

## How to Contribute

### Reporting Bugs

1. Check if the bug has already been reported in [Issues](https://github.com/MouaadhW/ai-call-center-system/issues)
2. If not, create a new issue with:
   - Clear title and description
   - Steps to reproduce
   - Expected vs actual behavior
   - System information (OS, Docker version, etc.)
   - Relevant logs

### Suggesting Features

1. Open an issue with the `enhancement` label
2. Describe the feature and its use case
3. Explain why it would be valuable

### Pull Requests

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Test thoroughly
5. Commit with clear messages (`git commit -m 'Add amazing feature'`)
6. Push to your fork (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## Code Style

- **Python**: Follow PEP 8
- **JavaScript**: Use ESLint configuration
- **Comments**: Write clear, concise comments
- **Documentation**: Update docs for any API changes

## Testing

- Write tests for new features
- Ensure all tests pass: `pytest`
- Test manually with the system running

## Development Setup

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/ai-call-center-system.git
cd ai-call-center-system

# Create environment
cp .env.example .env

# Start development environment
docker-compose up -d

# Run tests
docker exec -it backend pytest
```

## Questions?

Feel free to open an issue or reach out!

Thank you for contributing! 🙏
