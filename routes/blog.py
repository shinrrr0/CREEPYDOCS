"""
Blog blueprint: post feed + creation.

Thin view functions – fetch data via PostRepository, pass to templates.
File upload and validation happen here; business logic goes in services/.
"""

import os
from datetime import datetime

from flask import Blueprint, current_app, render_template, request, jsonify, abort

from repositories.post_repository import PostRepository


blog_bp = Blueprint("blog", __name__)


@blog_bp.route("/blog")
def blog():
    """Blog feed – all posts, newest first."""
    posts = PostRepository.list_all()
    return render_template(
        "blog.html",
        posts=posts,
        nav_sections=current_app.config["NAV_SECTIONS"],
        active_section="blog",
    )


@blog_bp.route("/api/blog/post", methods=["POST"])
def create_post():
    """
    Create a new post. Expects form data: text, file (image).
    At least one must be provided.

    Returns JSON: { success: bool, post?: Post data, error?: str }
    """
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
    post = PostRepository.create(text=text, image_filename=image_filename)
    if not post:
        return jsonify({
            "success": False,
            "error": "Failed to create post"
        }), 500

    return jsonify({
        "success": True,
        "post": {
            "id": post.id,
            "text": post.text,
            "image_filename": post.image_filename,
            "created_at": post.created_at.isoformat(),
        }
    }), 201


# FUTURE routes to add:
#   @blog_bp.route("/blog/<int:post_id>")              - full post detail page
#   @blog_bp.route("/api/blog/post/<int:post_id>", methods=["DELETE"]) - delete post
#   @blog_bp.route("/api/blog/post/<int:post_id>/like", methods=["POST"])  - like post
#   @blog_bp.route("/api/blog/<int:post_id>/comments", methods=["GET", "POST"]) - comments
