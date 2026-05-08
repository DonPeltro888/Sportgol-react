#!/usr/bin/env bash
# =============================================================================
# SEO Portable Module — Copy Helper for ticketgol.com integration
# =============================================================================
# Usage:
#   ./copy_seo_module.sh /path/to/ticketgol/repo
#
# This script copies all SEO module files to a target project.
# Tested with FastAPI + React + MongoDB stack.
# =============================================================================

set -e

if [ -z "$1" ]; then
  echo "Usage: $0 <target_repo_root>"
  echo "Example: $0 /home/dev/ticketgol"
  exit 1
fi

TARGET="$1"
SOURCE="$(cd "$(dirname "$0")" && pwd)"

echo "📦 Copying SEO Portable Module from $SOURCE to $TARGET"
echo ""

# Ensure target dirs exist
mkdir -p "$TARGET/backend/routes"
mkdir -p "$TARGET/backend/services"
mkdir -p "$TARGET/frontend/src/pages/admin/seo/intelligence"
mkdir -p "$TARGET/frontend/src/components/admin"
mkdir -p "$TARGET/frontend/src/utils"

# ===== BACKEND =====
echo "[1/6] Copying backend routes..."
cp "$SOURCE/backend/routes/seo_admin.py"        "$TARGET/backend/routes/"
cp "$SOURCE/backend/routes/seo_targets.py"      "$TARGET/backend/routes/"
cp "$SOURCE/backend/routes/seo_tools.py"        "$TARGET/backend/routes/"
cp "$SOURCE/backend/routes/seo_intelligence.py" "$TARGET/backend/routes/"
cp "$SOURCE/backend/routes/cost_observatory.py" "$TARGET/backend/routes/"

echo "[2/6] Copying backend services..."
for f in seo_keys seo_crypto seo_tools_catalog seo_orchestrator seo_claude \
         seo_gemini seo_perplexity seo_deepl seo_dataforseo seo_validator \
         seo_entity_context seo_image_gen seo_topic_cluster seo_cannibalization \
         seo_hreflang seo_faq_generator seo_jsonld_validator \
         api_cost_tracker api_cost_observatory api_pricing api_alerts api_balance_checker; do
  cp "$SOURCE/backend/services/${f}.py" "$TARGET/backend/services/" 2>/dev/null \
    && echo "  ✓ ${f}.py" \
    || echo "  ⚠ ${f}.py NOT FOUND (skip)"
done

# ===== FRONTEND PAGES =====
echo "[3/6] Copying frontend pages..."
for f in SeoDashboard SeoApiTools SeoPagesList SeoTargetEditor SeoBulkRunner CostObservatory; do
  cp "$SOURCE/frontend/src/pages/admin/seo/${f}.jsx" "$TARGET/frontend/src/pages/admin/seo/" \
    && echo "  ✓ ${f}.jsx"
done

echo "[4/6] Copying intelligence pages..."
for f in SeoIntelligenceHub TopicCluster Cannibalization Hreflang FaqGenerator JsonLdValidator; do
  cp "$SOURCE/frontend/src/pages/admin/seo/intelligence/${f}.jsx" \
     "$TARGET/frontend/src/pages/admin/seo/intelligence/" \
    && echo "  ✓ intelligence/${f}.jsx"
done

# ===== FRONTEND COMPONENTS =====
echo "[5/6] Copying frontend components..."
cp "$SOURCE/frontend/src/components/SchemaOrg.jsx"          "$TARGET/frontend/src/components/" 2>/dev/null && echo "  ✓ SchemaOrg.jsx"
cp "$SOURCE/frontend/src/components/TrustScoreBadge.jsx"    "$TARGET/frontend/src/components/" 2>/dev/null && echo "  ✓ TrustScoreBadge.jsx"
cp "$SOURCE/frontend/src/components/SeoContentBlock.jsx"    "$TARGET/frontend/src/components/" 2>/dev/null && echo "  ✓ SeoContentBlock.jsx"
cp "$SOURCE/frontend/src/components/SeoSchemaInjector.jsx"  "$TARGET/frontend/src/components/" 2>/dev/null && echo "  ✓ SeoSchemaInjector.jsx"
cp "$SOURCE/frontend/src/components/admin/SeoTargetSelector.jsx"     "$TARGET/frontend/src/components/admin/" 2>/dev/null && echo "  ✓ admin/SeoTargetSelector.jsx"
cp "$SOURCE/frontend/src/components/admin/SeoFilterStatusPanel.jsx"  "$TARGET/frontend/src/components/admin/" 2>/dev/null && echo "  ✓ admin/SeoFilterStatusPanel.jsx"

# ===== FRONTEND UTILS =====
echo "[6/6] Copying utils..."
cp "$SOURCE/frontend/src/utils/seoHero.js" "$TARGET/frontend/src/utils/" 2>/dev/null && echo "  ✓ seoHero.js"

# ===== DOC =====
cp "$SOURCE/SEO_PORTABLE_MODULE.md" "$TARGET/" 2>/dev/null && echo "  ✓ SEO_PORTABLE_MODULE.md (docs)"

echo ""
echo "✅ DONE!"
echo ""
echo "Next steps:"
echo "1. Add EMERGENT_LLM_KEY and SEO_FERNET_KEY to $TARGET/backend/.env"
echo "   Generate Fernet key:"
echo '   python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"'
echo ""
echo "2. Install Python deps in $TARGET/backend/:"
echo "   pip install httpx motor pydantic apscheduler rapidfuzz cryptography"
echo "   pip install emergentintegrations --extra-index-url https://d33sy5i8bnduwe.cloudfront.net/simple/"
echo ""
echo "3. Install npm deps in $TARGET/frontend/:"
echo "   yarn add lucide-react sonner react-router-dom"
echo ""
echo "4. Register routes in $TARGET/backend/server.py:"
echo "   from routes import seo_admin, seo_targets, seo_tools, seo_intelligence, cost_observatory"
echo "   app.include_router(seo_admin.router)"
echo "   app.include_router(seo_targets.router)"
echo "   app.include_router(seo_tools.router)"
echo "   app.include_router(seo_intelligence.router)"
echo "   app.include_router(cost_observatory.router)"
echo ""
echo "5. Read $TARGET/SEO_PORTABLE_MODULE.md for full integration guide."
echo ""
