package com.example.productreview;

import jakarta.persistence.*;
import java.time.OffsetDateTime;

@Entity
@Table(name = "product_review")
public class ProductReview {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Integer id;

    @Column(name = "product_id", nullable = false)
    private Integer productId;

    @Column(name = "rating", nullable = false)
    private Integer rating;

    @Column(name = "comment")
    private String comment;

    @Column(name = "author_name")
    private String authorName;

    @Column(name = "offer_id")
    private Integer offerId;

    @Column(name = "created_at", nullable = false)
    private OffsetDateTime createdAt;

    public Integer getId() { return id; }
    public Integer getProductId() { return productId; }
    public Integer getRating() { return rating; }
    public String getComment() { return comment; }
    public String getAuthorName() { return authorName; }
    public Integer getOfferId() { return offerId; }
    public OffsetDateTime getCreatedAt() { return createdAt; }

    public void setProductId(Integer productId) { this.productId = productId; }
    public void setRating(Integer rating) { this.rating = rating; }
    public void setComment(String comment) { this.comment = comment; }
    public void setAuthorName(String authorName) { this.authorName = authorName; }
    public void setOfferId(Integer offerId) { this.offerId = offerId; }
    public void setCreatedAt(OffsetDateTime createdAt) { this.createdAt = createdAt; }
}
