package com.example.productreview;

import java.time.OffsetDateTime;

public class ProductReview {

    private String id;
    private Integer productId;
    private Integer rating;
    private String comment;
    private String authorName;
    private Integer offerId;
    private OffsetDateTime createdAt;

    public String getId() { return id; }
    public Integer getProductId() { return productId; }
    public Integer getRating() { return rating; }
    public String getComment() { return comment; }
    public String getAuthorName() { return authorName; }
    public Integer getOfferId() { return offerId; }
    public OffsetDateTime getCreatedAt() { return createdAt; }

    public void setId(String id) { this.id = id; }
    public void setProductId(Integer productId) { this.productId = productId; }
    public void setRating(Integer rating) { this.rating = rating; }
    public void setComment(String comment) { this.comment = comment; }
    public void setAuthorName(String authorName) { this.authorName = authorName; }
    public void setOfferId(Integer offerId) { this.offerId = offerId; }
    public void setCreatedAt(OffsetDateTime createdAt) { this.createdAt = createdAt; }
}
