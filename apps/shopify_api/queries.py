"""GraphQL query and mutation documents for Shopify Admin API."""

PRODUCTS_QUERY = """
query GetProducts($first: Int!, $query: String) {
  products(first: $first, query: $query) {
    edges {
      node {
        id
        title
        handle
        description
        status
        totalInventory
        variants(first: 10) {
          edges {
            node {
              id
              title
              price
              sku
              availableForSale
            }
          }
        }
      }
    }
    pageInfo {
      hasNextPage
      endCursor
    }
  }
}
"""

PRODUCT_BY_ID_QUERY = """
query GetProductById($id: ID!) {
  product(id: $id) {
    id
    title
    handle
    description
    status
    totalInventory
    createdAt
    updatedAt
    vendor
    productType
    tags
    variants(first: 20) {
      edges {
        node {
          id
          title
          price
          sku
          barcode
          inventoryQuantity
          availableForSale
        }
      }
    }
  }
}
"""

INVENTORY_ITEMS_QUERY = """
query GetInventoryItems($first: Int!, $query: String) {
  inventoryItems(first: $first, query: $query) {
    edges {
      node {
        id
        sku
        tracked
        inventoryLevels(first: 5) {
          edges {
            node {
              id
              quantities(names: ["available", "incoming", "committed", "on_hand"]) {
                name
                quantity
              }
              location {
                id
                name
              }
            }
          }
        }
      }
    }
  }
}
"""

ORDERS_QUERY = """
query GetOrders($first: Int!, $query: String) {
  orders(first: $first, query: $query, sortKey: CREATED_AT, reverse: true) {
    edges {
      node {
        id
        name
        createdAt
        displayFinancialStatus
        displayFulfillmentStatus
        totalPriceSet {
          shopMoney {
            amount
            currencyCode
          }
        }
        customer {
          id
          displayName
          email
        }
        lineItems(first: 10) {
          edges {
            node {
              id
              title
              quantity
              variant {
                id
                title
                sku
              }
            }
          }
        }
      }
    }
    pageInfo {
      hasNextPage
      endCursor
    }
  }
}
"""

ORDER_BY_ID_QUERY = """
query GetOrderById($id: ID!) {
  order(id: $id) {
    id
    name
    createdAt
    displayFinancialStatus
    displayFulfillmentStatus
    note
    totalPriceSet {
      shopMoney {
        amount
        currencyCode
      }
    }
    customer {
      id
      displayName
      email
      phone
    }
    shippingAddress {
      address1
      city
      province
      country
      zip
    }
    lineItems(first: 50) {
      edges {
        node {
          id
          title
          quantity
          originalUnitPriceSet {
            shopMoney {
              amount
              currencyCode
            }
          }
        }
      }
    }
  }
}
"""

DRAFT_ORDER_CREATE_MUTATION = """
mutation CreateDraftOrder($input: DraftOrderInput!) {
  draftOrderCreate(input: $input) {
    draftOrder {
      id
      name
      status
      totalPrice
      invoiceUrl
      lineItems(first: 10) {
        edges {
          node {
            title
            quantity
            originalUnitPrice
          }
        }
      }
    }
    userErrors {
      field
      message
    }
  }
}
"""
