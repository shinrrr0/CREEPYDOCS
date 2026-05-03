"""
Blog blueprint: multi-blog posts with random blog redirection.

Architecture:
  - Multiple blogs identified by numeric IDs (1..MAX_BLOGS)
  - Each blog is lazy-created (no empty blogs in DB)
  - Multiple users can post to the same blog and see each other's posts
  - /blog/random redirects to a random blog number
  - /blog/<id> shows posts for blog <id> (empty is OK)

Thin view functions – fetch data via PostRepository, pass to templates.
File upload and validation happen here; business logic goes in services/.
"""

import os
import random
from datetime import datetime

from flask import Blueprint, current_app, render_template, request, jsonify, abort, redirect, url_for

from repositories.post_repository import PostRepository


blog_bp = Blueprint("blog", __name__)


@blog_bp.route("/blog/random")
def random_blog():
    """Redirect to a random blog (1 to MAX_BLOGS)."""
    max_blogs = current_app.config.get("MAX_BLOGS", 100)
    random_id = random.randint(1, max_blogs)
    return redirect(url_for("blog.blog_detail", blog_id=random_id))


@blog_bp.route("/blog/<int:blog_id>")
def blog_detail(blog_id: int):
    """Show posts for a specific blog."""
    max_blogs = current_app.config.get("MAX_BLOGS", 100)
    if blog_id < 1 or blog_id > max_blogs:
        abort(404)

    posts = PostRepository.list_by_blog(blog_id)
    return render_template(
        "blog.html",
        blog_id=blog_id,
        posts=posts,
        nav_sections=current_app.config["NAV_SECTIONS"],
        active_section=None,
    )


@blog_bp.route("/api/blog/<int:blog_id>/post", methods=["POST"])
def create_post(blog_id: int):
    """
    Create a new post in a blog. Expects form data: text, file (image).
    At least one must be provided.

    Returns JSON: { success: bool, post?: Post data, error?: str }
    """
    max_blogs = current_app.config.get("MAX_BLOGS", 100)
    if blog_id < 1 or blog_id > max_blogs:
        return jsonify({"success": False, "error": "Invalid blog ID"}), 400

    text = request.form.get("text", "").strip()
    file = request.files.get("image")

    image_filename = None
    if file and file.filename:
        # Validate file type (simple: just check extension)
        allowed = {".jpg", ".jpeg", ".png", ".gif", ".webp"}
        _, ext = os.path.splitext(file.filename.lower())
        if ext not in allowed:
            return jsonify({
                "success": False,
                "error": "Only images allowed: jpg, png, gif, webp"
            }), 400

        # Generate safe filename: timestamp_originalname
        timestamp = int(datetime.utcnow().timestamp())
        image_filename = f"{timestamp}_{os.path.basename(file.filename)}"

        # Ensure blog images directory exists
        blog_dir = os.path.join(
            current_app.static_folder, "images", "blog"
        )
        os.makedirs(blog_dir, exist_ok=True)

        # Save file
        filepath = os.path.join(blog_dir, image_filename)
        file.save(filepath)

    # Validate: at least text or image
    if not text and not image_filename:
        return jsonify({
            "success": False,
            "error": "Post must have text or an image"
        }), 400

    # Create post
    post = PostRepository.create(blog_id=blog_id, text=text, image_filename=image_filename)
    if not post:
        return jsonify({
            "success": False,
            "error": "Failed to create post"
        }), 500

    return jsonify({
        "success": True,
        "post": {
            "id": post.id,
            "blog_id": post.blog_id,
            "text": post.text,
            "image_filename": post.image_filename,
            "created_at": post.created_at.isoformat(),
        }
    }), 201


# FUTURE routes to add:
#   @blog_bp.route("/blog/<int:blog_id>/<int:post_id>")    - full post detail page
#   @blog_bp.route("/api/blog/<int:blog_id>/post/<int:post_id>", methods=["DELETE"]) - delete post
#   @blog_bp.route("/api/blog/<int:blog_id>/post/<int:post_id>/like", methods=["POST"]) - like post
