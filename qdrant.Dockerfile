FROM qdrant/qdrant:latest

# Set timezone
ENV TZ=Asia/Manila

# Expose ports
EXPOSE 6333 6334

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:6333/health || exit 1

# Default command
CMD ["./qdrant"]