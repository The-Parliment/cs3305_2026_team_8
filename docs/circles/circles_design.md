# Circles Service Design

The Circles microservice handles everything related to Circles.
A circle is an exclusive group. Each user has their own circle, and they can invite any of their friends to the circle. It is a group for close friends.

NOTE: For all GET requests to Circle API endpoints, claims from Depends(decode_and_verify) must be included.
