# Houdini Swap API Documentation

**Base URL:** `https://api-partner.houdiniswap.com`  
**Authentication:** All requests require a valid API key and secret for access.  
Authentication is done using an `Authorization` header using this syntax: `ApiKey:ApiSecret`

**Example:**
```
Authorization: ApiKey:ApiSecret
```

For full API specifications, refer to the [OpenAPI documentation](https://api-partner.houdiniswap.com/#/).

---

## Table of Contents

1. [Token Information APIs](#token-information-apis)
   - [Get CEX Tokens](#1-get-cex-tokens)
   - [Get DEX Tokens](#2-get-dex-tokens)
2. [Quote APIs](#quote-apis)
   - [Get CEX Quote](#3-get-cex-quote)
   - [Get DEX Quote](#4-get-dex-quote)
3. [Exchange Execution APIs](#exchange-execution-apis)
   - [Post CEX Exchange](#5-post-cex-exchange)
   - [Post DEX Exchange](#6-post-dex-exchange)
4. [DEX Transaction Management APIs](#dex-transaction-management-apis)
   - [Post dexApprove](#7-post-dexapprove)
   - [Post dexConfirmTx](#8-post-dexconfirmtx)
5. [Status and Information APIs](#status-and-information-apis)
   - [Get Status](#9-get-status)
   - [Get Min-Max](#10-get-min-max)
   - [Get Volume](#11-get-volume)
   - [Get WeeklyVolume](#12-get-weeklyvolume)

---

## Token Information APIs

### 1. Get CEX Tokens

**Endpoint:** `GET /tokens`

Fetches a list of tokens supported by Houdini Swap for CEX exchanges, detailing their respective chains. This information is useful for constructing token selection interfaces in applications.

**Parameters:** None

**Example Request:**
```
GET /tokens
```

**Example Response:**
```json
[
  {
    "id": "USDT",
    "name": "Tether",
    "symbol": "USDT",
    "network": {
      "name": "Ethereum Mainnet",
      "shortName": "ETH",
      "addressValidation": "^(0x)[0-9A-Fa-f]{40}$",
      "memoNeeded": false,
      "explorerUrl": "https://etherscan.io/tx/",
      "addressUrl": "https://etherscan.io/address/",
      "priority": 1,
      "kind": "evm",
      "chainId": 1
    },
    "color": "#26a17b",
    "keyword": "usdt usdterc20 tether usdteth erc-20 erc20 eth",
    "displayName": "USDT (ETHEREUM)",
    "chain": 1,
    "address": "0xdac17f958d2ee523a2206206994597c13d831ec7",
    "hasMarkup": true,
    "networkPriority": 2,
    "icon": "https://...",
    "hasFixed": true,
    "hasFixedReverse": true
  }
]
```

**Response Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Unique identifier for the token |
| `name` | string | Full name of the token (e.g., Tether) |
| `symbol` | string | The ticker symbol representing the token (e.g., USDT) |
| `network` | object | The blockchain network associated with the token. See NetworkDTO below |
| `color` | string | Hex color code associated with the token (deprecated) |
| `keyword` | string | Keywords related to the token for searchability |
| `displayName` | string | A user-friendly display name for the token |
| `icon` | string | URL for the token's icon |
| `hasFixed` | boolean | Indicates if the token supports fixed swap (deprecated) |
| `hasFixedReverse` | boolean | Indicates if the token supports fixed swaps in reverse (deprecated) |

**NetworkDTO Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `name` | string | Full name of the blockchain network (e.g., Ethereum Mainnet) |
| `shortName` | string | Short identifier for the network (e.g., ETH) |
| `memoNeeded` | boolean | Indicates if a memo or extra ID is required for transactions |
| `addressValidation` | string | Regular expression pattern for address validation on this network |
| `explorerUrl` | string | URL template for transaction explorer |
| `addressUrl` | string | URL template for address explorer |
| `priority` | number | Network priority |
| `kind` | string | Network kind (e.g., "evm") |
| `chainId` | number | Chain ID |

---

### 2. Get DEX Tokens

**Endpoint:** `GET /dexTokens`

Fetches a list of tokens supported for DEX exchanges.

**Parameters:**

| Name | Type | Location | Description | Default | Example |
|------|------|----------|-------------|---------|---------|
| `page` | number | query | Page number | `1` | `1` |
| `pageSize` | number | query | Number of tokens per page | `100` | `100` |
| `chain` | string | query | Chain short name (e.g., base) | *(none)* | `base` |

**Example Request:**
```
GET /dexTokens?page=1&pageSize=100&chain=base
```

**Example Response:**
```json
{
  "count": 1,
  "tokens": [
    {
      "id": "66cf5512ba629b6c861a7f45",
      "address": "0xE3086852A4B125803C815a158249ae468A3254Ca",
      "chain": "base",
      "decimals": 18,
      "symbol": "mfer",
      "name": "mfer",
      "created": "2024-08-28T16:49:22.854Z",
      "modified": "2024-09-04T13:42:03.030Z",
      "enabled": true,
      "hasDex": true
    }
  ]
}
```

**Response Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `count` | number | Total number of tokens |
| `tokens` | array | Array of token objects |
| `tokens[].id` | string | Unique identifier for the token |
| `tokens[].address` | string | Blockchain address of the token |
| `tokens[].chain` | string | The chain on which the token exists (e.g., `base`) |
| `tokens[].decimals` | number | Number of decimal places the token uses |
| `tokens[].symbol` | string | Token symbol (e.g., `mfer`) |
| `tokens[].name` | string | Full name of the token |
| `tokens[].created` | string | Timestamp of when the token was added (ISO 8601 format) |
| `tokens[].modified` | string | Timestamp of the last modification (ISO 8601 format) |
| `tokens[].enabled` | boolean | Whether the token is enabled for use |
| `tokens[].hasDex` | boolean | Indicates if the token supports DEX trading |

---

## Quote APIs

### 3. Get CEX Quote

**Endpoint:** `GET /quote`

Gets a quote for a CEX exchange transaction.

**Parameters:**

| Field | Type | Description |
|-------|------|-------------|
| `amount` | string | The amount which the client is willing to transfer (Example: 2) |
| `from` | string | The TokenID of a currency the client will transfer (Example: BNB) |
| `to` | string | The TokenID of a currency the client will receive (Example: ETH) |
| `anonymous` | boolean | Anonymous / Non-anonymous flow. For Anonymous, it will go through a `XMR` route |
| `useXmr` | boolean (optional) | Use XMR if it is true or if it is false use another token for the anonymous transaction for the quote or exchange |

**Example Request:**
```
GET /quote?amount=2&from=ETH&to=BNB&anonymous=false&useXmr=false
```

**Example Response:**
```json
{
  "amountIn": 2,
  "amountOut": 12345,
  "min": 0.1,
  "max": 99999999,
  "useXmr": false,
  "duration": 15
}
```

**Response Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `amountIn` | number | Quoted amount in |
| `amountOut` | number | Quoted amount out |
| `deviceInfo` | string (optional) | Device info type (e.g., Linux, Windows) |
| `isMobile` | boolean (optional) | Indicates if the request is from a mobile device |
| `clientId` | string (optional) | Client ID |
| `min` | number | Minimum amount accepted for exchange |
| `max` | number | Maximum amount accepted for exchange |
| `useXmr` | boolean | Use XMR if `true`, otherwise use another token for an anonymous transaction |
| `duration` | number | Duration of the exchange in minutes |

---

### 4. Get DEX Quote

**Endpoint:** `GET /dexQuote`

Gets a quote for a DEX exchange transaction.

**Parameters:**

| Field | Type | Description |
|-------|------|-------------|
| `amount` | string | Id of the token from which the swap is initiated (Example: 100) |
| `tokenIdFrom` | string | Id of the token from which the swap is initiated (Example: 6689b73ec90e45f3b3e51553) |
| `tokenIdTo` | string | Id of the token to which the swap is directed (Example: 6689b73ec90e45f3b3e51558) |

**Example Request:**
```
GET /dexQuote?amount=100&tokenIdFrom=6689b73ec90e45f3b3e51553&tokenIdTo=6689b73ec90e45f3b3e51558
```

**Example Response:**
```json
[
  {
    "swap": "sw",
    "quoteId": "66fa78f90bf604337992cba9",
    "amountOut": 16.76282693,
    "amountOutUsd": 2589.019,
    "duration": 1,
    "gas": 5978057870193888,
    "feeUsd": 4.853,
    "path": ["debridge"],
    "raw": {
      "duration": 1,
      "gas": "5978057870193888",
      "quote": {
        "integration": "debridge",
        "type": "swap",
        "bridgeFee": "31425535",
        "bridgeFeeInNativeToken": "1000000000000000",
        "amount": "16762826930",
        "decimals": 9,
        "amountUSD": "2589.019",
        "bridgeFeeUSD": "4.853",
        "bridgeFeeInNativeTokenUSD": "2.606",
        "fees": [...]
      },
      "route": [
        {
          "bridge": "debridge",
          "bridgeTokenAddress": "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48",
          "steps": ["allowance", "approve", "send"],
          "name": "USDC",
          "part": 100
        }
      ],
      "distribution": {
        "debridge": 1
      },
      "gasUSD": "15.582"
    }
  }
]
```

**Response Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `swap` | string | Swap identifier |
| `quoteId` | string | Unique identifier for the quote |
| `amountOut` | number | Quoted amount out |
| `amountOutUsd` | number | Quoted amount out in USD |
| `duration` | number | Estimated duration of the swap in minutes |
| `gas` | number | Gas fee for the swap transaction |
| `feeUsd` | number | Fee amount in USD |
| `path` | array | Path taken for the swap |
| `raw` | object | Raw transaction data including gas and duration. See RouteDTO |

---

## Exchange Execution APIs

### 5. Post CEX Exchange

**Endpoint:** `POST /exchange`

Initiates a CEX exchange transaction.

**Request Body Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `amount` | number | Amount to be exchanged (example: 1) |
| `from` | string | Symbol of the input token (example: ETH) |
| `to` | string | Symbol of the output token (example: BNB) |
| `receiverTag` | string (optional) | Optional receiver tag (example: 123) |
| `anonymous` | boolean | Indicates if the transaction is anonymous (example: false) |
| `addressTo` | string | Destination address |
| `walletId` | string (optional) | User's wallet identifier |
| `ip` | string | User IP address. Used for fraud prevention only |
| `userAgent` | string | User userAgent browser string |
| `timezone` | string | User browser timezone (example: UTC) |
| `useXmr` | string (optional) | Use XMR if it is true or if it is false use another token for the anonymous transaction |

**Example Request:**
```json
POST /exchange
Content-Type: application/json

{
  "amount": 1,
  "from": "ETH",
  "to": "BNB",
  "receiverTag": "",
  "addressTo": "0x000000000000000000000000000000000000dead",
  "anonymous": false,
  "ip": "0.0.0.0",
  "userAgent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
  "timezone": "UTC",
  "useXmr": false
}
```

**Example Response:**
```json
{
  "houdiniId": "mNev2KrGikabTvge75GMwM",
  "created": "2025-02-21T15:32:53.821Z",
  "senderAddress": "0xabb5ac5c686d1614172ac1292519e78ad6c520f5",
  "receiverAddress": "0x000000000000000000000000000000000000dead",
  "anonymous": false,
  "expires": "2025-02-21T16:02:53.821Z",
  "status": 0,
  "inAmount": 1,
  "inSymbol": "ETH",
  "outAmount": 4.189816,
  "outSymbol": "BNB",
  "senderTag": "",
  "receiverTag": "",
  "notified": false,
  "eta": 5,
  "inAmountUsd": 2802.42,
  "inCreated": "2025-02-21T15:32:53.822Z",
  "quote": {
    "amountIn": 1,
    "amountOut": 4.189816,
    "min": 0.001,
    "max": 17.841,
    "path": "ff"
  },
  "outToken": { ... },
  "inToken": { ... }
}
```

**Response Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `houdiniId` | string | Unique identifier for the exchange transaction |
| `created` | string | Timestamp of when the transaction was created |
| `senderAddress` | string | Address of the sender |
| `receiverAddress` | string | Address of the receiver |
| `anonymous` | boolean | Indicates if the transaction is anonymous |
| `expires` | string | Expiration timestamp of the transaction |
| `status` | number | Status code of the transaction |
| `inAmount` | number | Amount sent in the exchange |
| `outAmount` | number | Amount received in the exchange |
| `inSymbol` | string | Symbol of the input token |
| `outSymbol` | string | Symbol of the output token |
| `senderTag` | string (optional) | Optional sender tag |
| `receiverTag` | string (optional) | Optional receiver tag |
| `notified` | boolean | Indicates if the user has been notified |
| `eta` | number | Estimated time of arrival (in minutes) |
| `inAmountUsd` | number | Input amount converted to USD |
| `inCreated` | string | Timestamp when the input was created |
| `quote` | object | Details of the exchange quote (amounts, min/max limits, path) |
| `outToken` | object | Details of the output token. See TokenDTO |
| `inToken` | object | Details of the input token. See TokenDTO |

---

### 6. Post DEX Exchange

**Endpoint:** `POST /dexExchange`

Initiates a DEX exchange transaction.

**Request Body Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `amount` | number | Amount to be exchanged (example: `0.2`) |
| `tokenIdTo` | string | ID of the output token (example: `6689b73ec90e45f3b3e51558`) |
| `tokenIdFrom` | string | ID of the input token (example: `6689b73ec90e45f3b3e51553`) |
| `addressTo` | string | Destination address (example: `H1DiPSsBVBpDG57q5ZnxhZpRrsPQBvZfrbFQth6wyGyw`) |
| `addressFrom` | string | Sender's address (example: `0x45CF73349a4895fabA18c0f51f06D79f0794898D`) |
| `swap` | string | Swap method (example: `sw`) |
| `quoteId` | string | Quote identifier (example: `66fa79723eccf00d849b48ed`) |
| `route` | object | Routing and fee details. See RouteDTO |

**Example Request:**
```json
POST /dexExchange
Content-Type: application/json

{
  "amount": 0.2,
  "tokenIdTo": "6689b73ec90e45f3b3e51558",
  "tokenIdFrom": "6689b73ec90e45f3b3e51553",
  "addressTo": "H1DiPSsBVBpDG57q5ZnxhZpRrsPQBvZfrbFQth6wyGyw",
  "addressFrom": "0x45CF73349a4895fabA18c0f51f06D79f0794898D",
  "swap": "sw",
  "quoteId": "66fa79723eccf00d849b48ed",
  "route": { ... }
}
```

**Example Response:**
```json
{
  "houdiniId": "h9NpKm75gRnX7GWaFATwYn",
  "created": "2024-10-08T12:22:25.843Z",
  "senderAddress": "0xe90cAc99ccab34A669fFC2eE4e9c0E5067dE29ac",
  "receiverAddress": "H1DiPSsBVBpDG57q5ZnxhZpRrsPQBvZfrbFQth6wyGyw",
  "anonymous": false,
  "expires": "2024-10-08T12:52:25.843Z",
  "status": 0,
  "inAmount": 50,
  "inSymbol": "6689b73ec90e45f3b3e51592",
  "outAmount": 0.266471241,
  "outSymbol": "6689b73ec90e45f3b3e51558",
  "senderTag": "",
  "receiverTag": "",
  "notified": false,
  "eta": 1,
  "inAmountUsd": 38.422,
  "inCreated": "2024-10-08T12:22:25.843Z",
  "quote": {
    "amountIn": 50,
    "amountOut": 0.266471241
  },
  "metadata": { ... },
  "isDex": true
}
```

**Response Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `houdiniId` | string | Unique transaction ID |
| `created` | string | Timestamp when transaction was created |
| `senderAddress` | string | Sender's wallet address |
| `receiverAddress` | string | Recipient's wallet address |
| `anonymous` | boolean | Indicates if transaction is anonymous |
| `expires` | string | Expiration timestamp |
| `status` | number | Status code |
| `inAmount` | number | Input amount |
| `inSymbol` | string | Input token symbol |
| `outAmount` | number | Output amount |
| `outSymbol` | string | Output token symbol |
| `eta` | number | Estimated time of arrival in minutes |
| `inAmountUsd` | number | Input amount in USD |
| `inCreated` | string | Timestamp when input was created |
| `quote` | object | Quoted exchange details |
| `metadata` | object | Additional metadata |
| `isDex` | boolean | Indicates if transaction is a DEX trade |

---

## DEX Transaction Management APIs

### 7. Post dexApprove

**Endpoint:** `POST /dexApprove`

This endpoint is used to initiate a token approval transaction for the DexExchange platform.

**Request Body Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `tokenIdTo` | string | Token identifier to which the swap is directed |
| `tokenIdFrom` | string | Token identifier from which the swap is initiated |
| `addressFrom` | string | Address from which the amount will be deducted |
| `amount` | number | Amount to be approved |
| `swap` | string | Swap identifier or type (example: ch) |
| `route` | object | see RouteDTO |

**Example Request:**
```json
POST /dexApprove
Content-Type: application/json

{
  "tokenIdTo": "6689b73ec90e45f3b3e51558",
  "tokenIdFrom": "6689b73ec90e45f3b3e51553",
  "addressFrom": "0x45CF73349a4895fabA18c0f51f06D79f0794898D",
  "amount": 1,
  "swap": "sw",
  "route": { ... }
}
```

**Example Response:**
```json
[
  {
    "data": "0x095ea7b300000000000000000000000072788af7fc87d14da73f94e353e52b76e230035b000000000000000000000000000000000000000000000000016345785d8a0000",
    "to": "0x0000000000000000000000000000000000000000",
    "from": "0x789",
    "fromChain": {
      "id": "667160411933f7647414f091",
      "created": "2024-06-18T10:24:01.870Z",
      "modified": "2024-09-04T13:41:54.131Z",
      "name": "Ethereum",
      "shortName": "ethereum",
      "addressValidation": "^(0x)[0-9A-Fa-f]{40}$",
      "explorerUrl": "https://etherscan.io/tx/{txHash}",
      "addressUrl": "https://etherscan.io/tokens/{address}",
      "kind": "evm",
      "chainId": 1,
      "block": "0",
      "gasPrice": "0",
      "lastBaseFeePerGas": "0",
      "maxFeePerGas": "0",
      "maxPriorityFeePerGas": "0",
      "enabled": true,
      "icon": "http://localhost:3000/assets/dexchains/667160411933f7647414f091.png"
    }
  }
]
```

**Response Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `data` | string | Transaction data |
| `to` | string | Token identifier to which the swap is directed |
| `from` | string | Token identifier from which the swap is initiated |
| `fromChain` | object | See ChainDTO |

**ChainDTO Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Chain ID |
| `created` | date-time | Chain created at |
| `modified` | date-time | Chain modified at |
| `name` | string | Chain name |
| `shortName` | string | Chain short name |
| `addressValidation` | string | Regex to validate the address |
| `memoNeeded` | boolean | Does the chain require a memo |
| `explorerUrl` | string | Explorer URL template |
| `addressUrl` | string | Address URL template |
| `icon` | string | Icon URL |
| `priority` | number | Priority |
| `kind` | string | Chain kind |
| `chainId` | number | Chain ID |
| `block` | bigint | Block number |
| `gasPrice` | bigint | Gas Price |
| `lastBaseFeePerGas` | bigint | Last base fee per gas |
| `maxFeePerGas` | bigint | Max fee per gas |
| `maxPriorityFeePerGas` | bigint | Max priority fee per gas |
| `enabled` | boolean | Is chain enabled |

---

### 8. Post dexConfirmTx

**Endpoint:** `POST /dexConfirmTx`

Confirms a DEX transaction.

**Parameters:** None

**Request Body Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Internal ID of the transaction |
| `txHash` | string | Blockchain transaction hash |

**Example Request:**
```json
POST /dexConfirmTx
Content-Type: application/json

{
  "id": "6689b73ec90e45f3b3e51553",
  "txHash": "0x123456789abcdef..."
}
```

**Example Response:**
```json
true
```

**Response Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `response` | boolean | Transaction confirmation response |

---

## Status and Information APIs

### 9. Get Status

**Endpoint:** `GET /status/{houdiniID}`

Gets the status of an exchange transaction.

**Parameters:**

| Field | Type | Description |
|-------|------|-------------|
| `houdiniId` | string | Unique ID of the transaction (example: `h9NpKm75gRnX7GWaFATwYn`) |

**Example Request:**
```
GET /status?id=fgCqqMztaiV8dyo6mLqYgx
```

**Status Codes:**

| Status Code | Description |
|-------------|-------------|
| `-1` | NEW |
| `0` | WAITING |
| `1` | CONFIRMING |
| `2` | EXCHANGING |
| `3` | ANONYMIZING |
| `4` | FINISHED |
| `5` | EXPIRED |
| `6` | FAILED |
| `7` | REFUNDED |
| `8` | DELETED |

---

### 10. Get Min-Max

**Endpoint:** `GET /getMinMax`

Gets minimum and maximum exchange amounts for token pairs.

**Parameters:**

| Field | Type | Description |
|-------|------|-------------|
| `from` | string | Symbol of the source token (example: ETH) |
| `to` | string | Symbol of the destination token (example: BNB) |
| `anonymous` | boolean | Indicates if the transaction should be anonymous (example: false) |
| `cexOnly` | boolean (optional) | Whether to limit results to centralized exchanges (example: false) |

**Example Request:**
```
GET /getMinMax?from=ETH&to=BNB&anonymous=false&cexOnly=false
```

**Example Response:**
```json
[
  0.0253712625,
  16.914175
]
```

**Response:** Array with two elements:
- First element: **minimum** exchangeable amount
- Second element: **maximum** exchangeable amount

---

### 11. Get Volume

**Endpoint:** `GET /volume`

Retrieves the total swap volume for HoudiniSwap.

**Parameters:** None

**Example Request:**
```
GET /volume
```

**Example Response:**
```json
[
  {
    "count": 0,
    "totalTransactedUSD": 0
  }
]
```

**Response Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `count` | number | The total number of transactions on the exchange |
| `totalTransactedUSD` | number | The total value in USD at the time of the swap |

---

### 12. Get WeeklyVolume

**Endpoint:** `GET /weeklyVolume`

Retrieves the weekly swap volume data for HoudiniSwap.

**Parameters:** None

**Example Request:**
```
GET /weeklyVolume
```

**Example Response:**
```json
[
  {
    "count": 0,
    "anonymous": 0,
    "volume": 0,
    "week": 0,
    "year": 0,
    "commission": 0
  }
]
```

**Response Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `count` | number | Total transactions count |
| `anonymous` | number | Total transactions that are anonymous (out of the total count) |
| `volume` | number | Total transactions volume in USD |
| `week` | number | Week of the year |
| `year` | number | Year number |
| `commission` | number | Commission in USD |

---

## Data Models

### TokenDTO
Token information structure. Referenced in multiple endpoints.

### NetworkDTO
Blockchain network information. Includes validation patterns, explorer URLs, and chain metadata.

### QuoteDTO
Quote response structure. Contains exchange rates, amounts, and validity information.

### RouteDTO
Routing and fee details for DEX transactions. Includes bridge information, gas estimates, and fee breakdowns.

For detailed schema definitions, refer to the [OpenAPI documentation](https://api-partner.houdiniswap.com/#/).

---

## Notes

- **dexAllowance:** The changelog mentions `dexAllowance` as a documented endpoint, but it does not exist as a separate API endpoint. "Allowance" appears as a step in the DEX exchange process workflow (within the route steps array), but there is no dedicated `/dexAllowance` endpoint. The functionality is handled through the `dexApprove` endpoint.

- **Authentication:** All requests require authentication using the `Authorization` header with format `ApiKey:ApiSecret`.

- **Base URL:** All endpoints are relative to `https://api-partner.houdiniswap.com`.

- **Rate Limiting:** Rate limits are not explicitly documented but should be considered when implementing the SDK.

---

*Documentation extracted from: https://docs.houdiniswap.com/houdini-swap/api-documentation/*  
*Last updated: 2025-12-23*

