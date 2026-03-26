--
-- File generated with SQLiteStudio v3.4.21 on Wed Mar 25 16:24:31 2026
--
-- Text encoding used: UTF-8
--
PRAGMA foreign_keys = off;
BEGIN TRANSACTION;

-- Table: country
CREATE TABLE IF NOT EXISTS country (
    id          INTEGER       NOT NULL,
    iso_code_2  VARCHAR (2)   NOT NULL,
    name        VARCHAR (45)  NOT NULL,
    description VARCHAR (255),
    region      VARCHAR (45),
    subregion   VARCHAR (45),
    CONSTRAINT pk_country PRIMARY KEY (
        id
    ),
    CONSTRAINT uq_country_iso_code_2 UNIQUE (
        iso_code_2
    ),
    CONSTRAINT uq_country_name UNIQUE (
        name
    )
);

INSERT INTO country (
                        id,
                        iso_code_2,
                        name,
                        description,
                        region,
                        subregion
                    )
                    VALUES (
                        1,
                        'CK',
                        'Cook Islands',
                        'Cook Islands',
                        'Oceania',
                        'Polynesia'
                    );

INSERT INTO country (
                        id,
                        iso_code_2,
                        name,
                        description,
                        region,
                        subregion
                    )
                    VALUES (
                        2,
                        'GN',
                        'Guinea',
                        'Republic of Guinea',
                        'Africa',
                        'Western Africa'
                    );

INSERT INTO country (
                        id,
                        iso_code_2,
                        name,
                        description,
                        region,
                        subregion
                    )
                    VALUES (
                        3,
                        'CX',
                        'Christmas Island',
                        'Territory of Christmas Island',
                        'Oceania',
                        'Australia and New Zealand'
                    );

INSERT INTO country (
                        id,
                        iso_code_2,
                        name,
                        description,
                        region,
                        subregion
                    )
                    VALUES (
                        4,
                        'TG',
                        'Togo',
                        'Togolese Republic',
                        'Africa',
                        'Western Africa'
                    );

INSERT INTO country (
                        id,
                        iso_code_2,
                        name,
                        description,
                        region,
                        subregion
                    )
                    VALUES (
                        5,
                        'TW',
                        'Taiwan',
                        'Republic of China (Taiwan)',
                        'Asia',
                        'Eastern Asia'
                    );

INSERT INTO country (
                        id,
                        iso_code_2,
                        name,
                        description,
                        region,
                        subregion
                    )
                    VALUES (
                        6,
                        'KG',
                        'Kyrgyzstan',
                        'Kyrgyz Republic',
                        'Asia',
                        'Central Asia'
                    );

INSERT INTO country (
                        id,
                        iso_code_2,
                        name,
                        description,
                        region,
                        subregion
                    )
                    VALUES (
                        7,
                        'SR',
                        'Suriname',
                        'Republic of Suriname',
                        'Americas',
                        'South America'
                    );

INSERT INTO country (
                        id,
                        iso_code_2,
                        name,
                        description,
                        region,
                        subregion
                    )
                    VALUES (
                        8,
                        'DO',
                        'Dominican Republic',
                        'Dominican Republic',
                        'Americas',
                        'Caribbean'
                    );

INSERT INTO country (
                        id,
                        iso_code_2,
                        name,
                        description,
                        region,
                        subregion
                    )
                    VALUES (
                        9,
                        'GT',
                        'Guatemala',
                        'Republic of Guatemala',
                        'Americas',
                        'Central America'
                    );

INSERT INTO country (
                        id,
                        iso_code_2,
                        name,
                        description,
                        region,
                        subregion
                    )
                    VALUES (
                        10,
                        'DZ',
                        'Algeria',
                        'People''s Democratic Republic of Algeria',
                        'Africa',
                        'Northern Africa'
                    );

INSERT INTO country (
                        id,
                        iso_code_2,
                        name,
                        description,
                        region,
                        subregion
                    )
                    VALUES (
                        11,
                        'UA',
                        'Ukraine',
                        'Ukraine',
                        'Europe',
                        'Eastern Europe'
                    );

INSERT INTO country (
                        id,
                        iso_code_2,
                        name,
                        description,
                        region,
                        subregion
                    )
                    VALUES (
                        12,
                        'KN',
                        'Saint Kitts and Nevis',
                        'Federation of Saint Christopher and Nevis',
                        'Americas',
                        'Caribbean'
                    );

INSERT INTO country (
                        id,
                        iso_code_2,
                        name,
                        description,
                        region,
                        subregion
                    )
                    VALUES (
                        13,
                        'HR',
                        'Croatia',
                        'Republic of Croatia',
                        'Europe',
                        'Southeast Europe'
                    );

INSERT INTO country (
                        id,
                        iso_code_2,
                        name,
                        description,
                        region,
                        subregion
                    )
                    VALUES (
                        14,
                        'GQ',
                        'Equatorial Guinea',
                        'Republic of Equatorial Guinea',
                        'Africa',
                        'Middle Africa'
                    );

INSERT INTO country (
                        id,
                        iso_code_2,
                        name,
                        description,
                        region,
                        subregion
                    )
                    VALUES (
                        15,
                        'PA',
                        'Panama',
                        'Republic of Panama',
                        'Americas',
                        'Central America'
                    );

INSERT INTO country (
                        id,
                        iso_code_2,
                        name,
                        description,
                        region,
                        subregion
                    )
                    VALUES (
                        16,
                        'BE',
                        'Belgium',
                        'Kingdom of Belgium',
                        'Europe',
                        'Western Europe'
                    );

INSERT INTO country (
                        id,
                        iso_code_2,
                        name,
                        description,
                        region,
                        subregion
                    )
                    VALUES (
                        17,
                        'BV',
                        'Bouvet Island',
                        'Bouvet Island',
                        'Antarctic',
                        NULL
                    );

INSERT INTO country (
                        id,
                        iso_code_2,
                        name,
                        description,
                        region,
                        subregion
                    )
                    VALUES (
                        18,
                        'RW',
                        'Rwanda',
                        'Republic of Rwanda',
                        'Africa',
                        'Eastern Africa'
                    );

INSERT INTO country (
                        id,
                        iso_code_2,
                        name,
                        description,
                        region,
                        subregion
                    )
                    VALUES (
                        19,
                        'TF',
                        'French Southern and Antarctic Lands',
                        'Territory of the French Southern and Antarctic Lands',
                        'Antarctic',
                        NULL
                    );

INSERT INTO country (
                        id,
                        iso_code_2,
                        name,
                        description,
                        region,
                        subregion
                    )
                    VALUES (
                        20,
                        'CV',
                        'Cape Verde',
                        'Republic of Cabo Verde',
                        'Africa',
                        'Western Africa'
                    );

INSERT INTO country (
                        id,
                        iso_code_2,
                        name,
                        description,
                        region,
                        subregion
                    )
                    VALUES (
                        21,
                        'KR',
                        'South Korea',
                        'Republic of Korea',
                        'Asia',
                        'Eastern Asia'
                    );

INSERT INTO country (
                        id,
                        iso_code_2,
                        name,
                        description,
                        region,
                        subregion
                    )
                    VALUES (
                        22,
                        'GU',
                        'Guam',
                        'Guam',
                        'Oceania',
                        'Micronesia'
                    );

INSERT INTO country (
                        id,
                        iso_code_2,
                        name,
                        description,
                        region,
                        subregion
                    )
                    VALUES (
                        23,
                        'AD',
                        'Andorra',
                        'Principality of Andorra',
                        'Europe',
                        'Southern Europe'
                    );

INSERT INTO country (
                        id,
                        iso_code_2,
                        name,
                        description,
                        region,
                        subregion
                    )
                    VALUES (
                        24,
                        'SN',
                        'Senegal',
                        'Republic of Senegal',
                        'Africa',
                        'Western Africa'
                    );

INSERT INTO country (
                        id,
                        iso_code_2,
                        name,
                        description,
                        region,
                        subregion
                    )
                    VALUES (
                        25,
                        'UY',
                        'Uruguay',
                        'Oriental Republic of Uruguay',
                        'Americas',
                        'South America'
                    );

INSERT INTO country (
                        id,
                        iso_code_2,
                        name,
                        description,
                        region,
                        subregion
                    )
                    VALUES (
                        26,
                        'CG',
                        'Republic of the Congo',
                        'Republic of the Congo',
                        'Africa',
                        'Middle Africa'
                    );

INSERT INTO country (
                        id,
                        iso_code_2,
                        name,
                        description,
                        region,
                        subregion
                    )
                    VALUES (
                        27,
                        'NA',
                        'Namibia',
                        'Republic of Namibia',
                        'Africa',
                        'Southern Africa'
                    );

INSERT INTO country (
                        id,
                        iso_code_2,
                        name,
                        description,
                        region,
                        subregion
                    )
                    VALUES (
                        28,
                        'SG',
                        'Singapore',
                        'Republic of Singapore',
                        'Asia',
                        'South-Eastern Asia'
                    );

INSERT INTO country (
                        id,
                        iso_code_2,
                        name,
                        description,
                        region,
                        subregion
                    )
                    VALUES (
                        29,
                        'FI',
                        'Finland',
                        'Republic of Finland',
                        'Europe',
                        'Northern Europe'
                    );

INSERT INTO country (
                        id,
                        iso_code_2,
                        name,
                        description,
                        region,
                        subregion
                    )
                    VALUES (
                        30,
                        'EG',
                        'Egypt',
                        'Arab Republic of Egypt',
                        'Africa',
                        'Northern Africa'
                    );

INSERT INTO country (
                        id,
                        iso_code_2,
                        name,
                        description,
                        region,
                        subregion
                    )
                    VALUES (
                        31,
                        'PW',
                        'Palau',
                        'Republic of Palau',
                        'Oceania',
                        'Micronesia'
                    );

INSERT INTO country (
                        id,
                        iso_code_2,
                        name,
                        description,
                        region,
                        subregion
                    )
                    VALUES (
                        32,
                        'AS',
                        'American Samoa',
                        'American Samoa',
                        'Oceania',
                        'Polynesia'
                    );

INSERT INTO country (
                        id,
                        iso_code_2,
                        name,
                        description,
                        region,
                        subregion
                    )
                    VALUES (
                        33,
                        'AG',
                        'Antigua and Barbuda',
                        'Antigua and Barbuda',
                        'Americas',
                        'Caribbean'
                    );

INSERT INTO country (
                        id,
                        iso_code_2,
                        name,
                        description,
                        region,
                        subregion
                    )
                    VALUES (
                        34,
                        'SC',
                        'Seychelles',
                        'Republic of Seychelles',
                        'Africa',
                        'Eastern Africa'
                    );

INSERT INTO country (
                        id,
                        iso_code_2,
                        name,
                        description,
                        region,
                        subregion
                    )
                    VALUES (
                        35,
                        'KW',
                        'Kuwait',
                        'State of Kuwait',
                        'Asia',
                        'Western Asia'
                    );

INSERT INTO country (
                        id,
                        iso_code_2,
                        name,
                        description,
                        region,
                        subregion
                    )
                    VALUES (
                        36,
                        'GR',
                        'Greece',
                        'Hellenic Republic',
                        'Europe',
                        'Southern Europe'
                    );

INSERT INTO country (
                        id,
                        iso_code_2,
                        name,
                        description,
                        region,
                        subregion
                    )
                    VALUES (
                        37,
                        'KI',
                        'Kiribati',
                        'Independent and Sovereign Republic of Kiribati',
                        'Oceania',
                        'Micronesia'
                    );

INSERT INTO country (
                        id,
                        iso_code_2,
                        name,
                        description,
                        region,
                        subregion
                    )
                    VALUES (
                        38,
                        'CY',
                        'Cyprus',
                        'Republic of Cyprus',
                        'Europe',
                        'Southern Europe'
                    );

INSERT INTO country (
                        id,
                        iso_code_2,
                        name,
                        description,
                        region,
                        subregion
                    )
                    VALUES (
                        39,
                        'ML',
                        'Mali',
                        'Republic of Mali',
                        'Africa',
                        'Western Africa'
                    );

INSERT INTO country (
                        id,
                        iso_code_2,
                        name,
                        description,
                        region,
                        subregion
                    )
                    VALUES (
                        40,
                        'BM',
                        'Bermuda',
                        'Bermuda',
                        'Americas',
                        'North America'
                    );

INSERT INTO country (
                        id,
                        iso_code_2,
                        name,
                        description,
                        region,
                        subregion
                    )
                    VALUES (
                        41,
                        'GL',
                        'Greenland',
                        'Greenland',
                        'Americas',
                        'North America'
                    );

INSERT INTO country (
                        id,
                        iso_code_2,
                        name,
                        description,
                        region,
                        subregion
                    )
                    VALUES (
                        42,
                        'ER',
                        'Eritrea',
                        'State of Eritrea',
                        'Africa',
                        'Eastern Africa'
                    );

INSERT INTO country (
                        id,
                        iso_code_2,
                        name,
                        description,
                        region,
                        subregion
                    )
                    VALUES (
                        43,
                        'TZ',
                        'Tanzania',
                        'United Republic of Tanzania',
                        'Africa',
                        'Eastern Africa'
                    );

INSERT INTO country (
                        id,
                        iso_code_2,
                        name,
                        description,
                        region,
                        subregion
                    )
                    VALUES (
                        44,
                        'VN',
                        'Vietnam',
                        'Socialist Republic of Vietnam',
                        'Asia',
                        'South-Eastern Asia'
                    );

INSERT INTO country (
                        id,
                        iso_code_2,
                        name,
                        description,
                        region,
                        subregion
                    )
                    VALUES (
                        45,
                        'TD',
                        'Chad',
                        'Republic of Chad',
                        'Africa',
                        'Middle Africa'
                    );

INSERT INTO country (
                        id,
                        iso_code_2,
                        name,
                        description,
                        region,
                        subregion
                    )
                    VALUES (
                        46,
                        'CI',
                        'Ivory Coast',
                        'Republic of Côte d''Ivoire',
                        'Africa',
                        'Western Africa'
                    );

INSERT INTO country (
                        id,
                        iso_code_2,
                        name,
                        description,
                        region,
                        subregion
                    )
                    VALUES (
                        47,
                        'GE',
                        'Georgia',
                        'Georgia',
                        'Asia',
                        'Western Asia'
                    );

INSERT INTO country (
                        id,
                        iso_code_2,
                        name,
                        description,
                        region,
                        subregion
                    )
                    VALUES (
                        48,
                        'IM',
                        'Isle of Man',
                        'Isle of Man',
                        'Europe',
                        'Northern Europe'
                    );

INSERT INTO country (
                        id,
                        iso_code_2,
                        name,
                        description,
                        region,
                        subregion
                    )
                    VALUES (
                        49,
                        'GS',
                        'South Georgia',
                        'South Georgia and the South Sandwich Islands',
                        'Antarctic',
                        NULL
                    );

INSERT INTO country (
                        id,
                        iso_code_2,
                        name,
                        description,
                        region,
                        subregion
                    )
                    VALUES (
                        50,
                        'BO',
                        'Bolivia',
                        'Plurinational State of Bolivia',
                        'Americas',
                        'South America'
                    );

INSERT INTO country (
                        id,
                        iso_code_2,
                        name,
                        description,
                        region,
                        subregion
                    )
                    VALUES (
                        51,
                        'UM',
                        'United States Minor Outlying Islands',
                        'United States Minor Outlying Islands',
                        'Americas',
                        'North America'
                    );

INSERT INTO country (
                        id,
                        iso_code_2,
                        name,
                        description,
                        region,
                        subregion
                    )
                    VALUES (
                        52,
                        'DK',
                        'Denmark',
                        'Kingdom of Denmark',
                        'Europe',
                        'Northern Europe'
                    );

INSERT INTO country (
                        id,
                        iso_code_2,
                        name,
                        description,
                        region,
                        subregion
                    )
                    VALUES (
                        53,
                        'TM',
                        'Turkmenistan',
                        'Turkmenistan',
                        'Asia',
                        'Central Asia'
                    );

INSERT INTO country (
                        id,
                        iso_code_2,
                        name,
                        description,
                        region,
                        subregion
                    )
                    VALUES (
                        54,
                        'NE',
                        'Niger',
                        'Republic of Niger',
                        'Africa',
                        'Western Africa'
                    );

INSERT INTO country (
                        id,
                        iso_code_2,
                        name,
                        description,
                        region,
                        subregion
                    )
                    VALUES (
                        55,
                        'FM',
                        'Micronesia',
                        'Federated States of Micronesia',
                        'Oceania',
                        'Micronesia'
                    );

INSERT INTO country (
                        id,
                        iso_code_2,
                        name,
                        description,
                        region,
                        subregion
                    )
                    VALUES (
                        56,
                        'JE',
                        'Jersey',
                        'Bailiwick of Jersey',
                        'Europe',
                        'Northern Europe'
                    );

INSERT INTO country (
                        id,
                        iso_code_2,
                        name,
                        description,
                        region,
                        subregion
                    )
                    VALUES (
                        57,
                        'KY',
                        'Cayman Islands',
                        'Cayman Islands',
                        'Americas',
                        'Caribbean'
                    );

INSERT INTO country (
                        id,
                        iso_code_2,
                        name,
                        description,
                        region,
                        subregion
                    )
                    VALUES (
                        58,
                        'LI',
                        'Liechtenstein',
                        'Principality of Liechtenstein',
                        'Europe',
                        'Western Europe'
                    );

INSERT INTO country (
                        id,
                        iso_code_2,
                        name,
                        description,
                        region,
                        subregion
                    )
                    VALUES (
                        59,
                        'BA',
                        'Bosnia and Herzegovina',
                        'Bosnia and Herzegovina',
                        'Europe',
                        'Southeast Europe'
                    );

INSERT INTO country (
                        id,
                        iso_code_2,
                        name,
                        description,
                        region,
                        subregion
                    )
                    VALUES (
                        60,
                        'FR',
                        'France',
                        'French Republic',
                        'Europe',
                        'Western Europe'
                    );

INSERT INTO country (
                        id,
                        iso_code_2,
                        name,
                        description,
                        region,
                        subregion
                    )
                    VALUES (
                        61,
                        'PF',
                        'French Polynesia',
                        'French Polynesia',
                        'Oceania',
                        'Polynesia'
                    );

INSERT INTO country (
                        id,
                        iso_code_2,
                        name,
                        description,
                        region,
                        subregion
                    )
                    VALUES (
                        62,
                        'KZ',
                        'Kazakhstan',
                        'Republic of Kazakhstan',
                        'Asia',
                        'Central Asia'
                    );

INSERT INTO country (
                        id,
                        iso_code_2,
                        name,
                        description,
                        region,
                        subregion
                    )
                    VALUES (
                        63,
                        'AO',
                        'Angola',
                        'Republic of Angola',
                        'Africa',
                        'Middle Africa'
                    );

INSERT INTO country (
                        id,
                        iso_code_2,
                        name,
                        description,
                        region,
                        subregion
                    )
                    VALUES (
                        64,
                        'NZ',
                        'New Zealand',
                        'New Zealand',
                        'Oceania',
                        'Australia and New Zealand'
                    );

INSERT INTO country (
                        id,
                        iso_code_2,
                        name,
                        description,
                        region,
                        subregion
                    )
                    VALUES (
                        65,
                        'PR',
                        'Puerto Rico',
                        'Commonwealth of Puerto Rico',
                        'Americas',
                        'Caribbean'
                    );

INSERT INTO country (
                        id,
                        iso_code_2,
                        name,
                        description,
                        region,
                        subregion
                    )
                    VALUES (
                        66,
                        'SA',
                        'Saudi Arabia',
                        'Kingdom of Saudi Arabia',
                        'Asia',
                        'Western Asia'
                    );

INSERT INTO country (
                        id,
                        iso_code_2,
                        name,
                        description,
                        region,
                        subregion
                    )
                    VALUES (
                        67,
                        'ME',
                        'Montenegro',
                        'Montenegro',
                        'Europe',
                        'Southeast Europe'
                    );

INSERT INTO country (
                        id,
                        iso_code_2,
                        name,
                        description,
                        region,
                        subregion
                    )
                    VALUES (
                        68,
                        'ZA',
                        'South Africa',
                        'Republic of South Africa',
                        'Africa',
                        'Southern Africa'
                    );

INSERT INTO country (
                        id,
                        iso_code_2,
                        name,
                        description,
                        region,
                        subregion
                    )
                    VALUES (
                        69,
                        'PK',
                        'Pakistan',
                        'Islamic Republic of Pakistan',
                        'Asia',
                        'Southern Asia'
                    );

INSERT INTO country (
                        id,
                        iso_code_2,
                        name,
                        description,
                        region,
                        subregion
                    )
                    VALUES (
                        70,
                        'LK',
                        'Sri Lanka',
                        'Democratic Socialist Republic of Sri Lanka',
                        'Asia',
                        'Southern Asia'
                    );

INSERT INTO country (
                        id,
                        iso_code_2,
                        name,
                        description,
                        region,
                        subregion
                    )
                    VALUES (
                        71,
                        'CM',
                        'Cameroon',
                        'Republic of Cameroon',
                        'Africa',
                        'Middle Africa'
                    );

INSERT INTO country (
                        id,
                        iso_code_2,
                        name,
                        description,
                        region,
                        subregion
                    )
                    VALUES (
                        72,
                        'GG',
                        'Guernsey',
                        'Bailiwick of Guernsey',
                        'Europe',
                        'Northern Europe'
                    );

INSERT INTO country (
                        id,
                        iso_code_2,
                        name,
                        description,
                        region,
                        subregion
                    )
                    VALUES (
                        73,
                        'LR',
                        'Liberia',
                        'Republic of Liberia',
                        'Africa',
                        'Western Africa'
                    );

INSERT INTO country (
                        id,
                        iso_code_2,
                        name,
                        description,
                        region,
                        subregion
                    )
                    VALUES (
                        74,
                        'AE',
                        'United Arab Emirates',
                        'United Arab Emirates',
                        'Asia',
                        'Western Asia'
                    );

INSERT INTO country (
                        id,
                        iso_code_2,
                        name,
                        description,
                        region,
                        subregion
                    )
                    VALUES (
                        75,
                        'CH',
                        'Switzerland',
                        'Swiss Confederation',
                        'Europe',
                        'Western Europe'
                    );

INSERT INTO country (
                        id,
                        iso_code_2,
                        name,
                        description,
                        region,
                        subregion
                    )
                    VALUES (
                        76,
                        'HU',
                        'Hungary',
                        'Hungary',
                        'Europe',
                        'Central Europe'
                    );

INSERT INTO country (
                        id,
                        iso_code_2,
                        name,
                        description,
                        region,
                        subregion
                    )
                    VALUES (
                        77,
                        'LY',
                        'Libya',
                        'State of Libya',
                        'Africa',
                        'Northern Africa'
                    );

INSERT INTO country (
                        id,
                        iso_code_2,
                        name,
                        description,
                        region,
                        subregion
                    )
                    VALUES (
                        78,
                        'VU',
                        'Vanuatu',
                        'Republic of Vanuatu',
                        'Oceania',
                        'Melanesia'
                    );

INSERT INTO country (
                        id,
                        iso_code_2,
                        name,
                        description,
                        region,
                        subregion
                    )
                    VALUES (
                        79,
                        'WF',
                        'Wallis and Futuna',
                        'Territory of the Wallis and Futuna Islands',
                        'Oceania',
                        'Polynesia'
                    );

INSERT INTO country (
                        id,
                        iso_code_2,
                        name,
                        description,
                        region,
                        subregion
                    )
                    VALUES (
                        80,
                        'LC',
                        'Saint Lucia',
                        'Saint Lucia',
                        'Americas',
                        'Caribbean'
                    );

INSERT INTO country (
                        id,
                        iso_code_2,
                        name,
                        description,
                        region,
                        subregion
                    )
                    VALUES (
                        81,
                        'CF',
                        'Central African Republic',
                        'Central African Republic',
                        'Africa',
                        'Middle Africa'
                    );

INSERT INTO country (
                        id,
                        iso_code_2,
                        name,
                        description,
                        region,
                        subregion
                    )
                    VALUES (
                        82,
                        'TJ',
                        'Tajikistan',
                        'Republic of Tajikistan',
                        'Asia',
                        'Central Asia'
                    );

INSERT INTO country (
                        id,
                        iso_code_2,
                        name,
                        description,
                        region,
                        subregion
                    )
                    VALUES (
                        83,
                        'IE',
                        'Ireland',
                        'Republic of Ireland',
                        'Europe',
                        'Northern Europe'
                    );

INSERT INTO country (
                        id,
                        iso_code_2,
                        name,
                        description,
                        region,
                        subregion
                    )
                    VALUES (
                        84,
                        'NC',
                        'New Caledonia',
                        'New Caledonia',
                        'Oceania',
                        'Melanesia'
                    );

INSERT INTO country (
                        id,
                        iso_code_2,
                        name,
                        description,
                        region,
                        subregion
                    )
                    VALUES (
                        85,
                        'YE',
                        'Yemen',
                        'Republic of Yemen',
                        'Asia',
                        'Western Asia'
                    );

INSERT INTO country (
                        id,
                        iso_code_2,
                        name,
                        description,
                        region,
                        subregion
                    )
                    VALUES (
                        86,
                        'FO',
                        'Faroe Islands',
                        'Faroe Islands',
                        'Europe',
                        'Northern Europe'
                    );

INSERT INTO country (
                        id,
                        iso_code_2,
                        name,
                        description,
                        region,
                        subregion
                    )
                    VALUES (
                        87,
                        'CU',
                        'Cuba',
                        'Republic of Cuba',
                        'Americas',
                        'Caribbean'
                    );

INSERT INTO country (
                        id,
                        iso_code_2,
                        name,
                        description,
                        region,
                        subregion
                    )
                    VALUES (
                        88,
                        'AZ',
                        'Azerbaijan',
                        'Republic of Azerbaijan',
                        'Asia',
                        'Western Asia'
                    );

INSERT INTO country (
                        id,
                        iso_code_2,
                        name,
                        description,
                        region,
                        subregion
                    )
                    VALUES (
                        89,
                        'SB',
                        'Solomon Islands',
                        'Solomon Islands',
                        'Oceania',
                        'Melanesia'
                    );

INSERT INTO country (
                        id,
                        iso_code_2,
                        name,
                        description,
                        region,
                        subregion
                    )
                    VALUES (
                        90,
                        'JM',
                        'Jamaica',
                        'Jamaica',
                        'Americas',
                        'Caribbean'
                    );

INSERT INTO country (
                        id,
                        iso_code_2,
                        name,
                        description,
                        region,
                        subregion
                    )
                    VALUES (
                        91,
                        'MA',
                        'Morocco',
                        'Kingdom of Morocco',
                        'Africa',
                        'Northern Africa'
                    );

INSERT INTO country (
                        id,
                        iso_code_2,
                        name,
                        description,
                        region,
                        subregion
                    )
                    VALUES (
                        92,
                        'TT',
                        'Trinidad and Tobago',
                        'Republic of Trinidad and Tobago',
                        'Americas',
                        'Caribbean'
                    );

INSERT INTO country (
                        id,
                        iso_code_2,
                        name,
                        description,
                        region,
                        subregion
                    )
                    VALUES (
                        93,
                        'YT',
                        'Mayotte',
                        'Department of Mayotte',
                        'Africa',
                        'Eastern Africa'
                    );

INSERT INTO country (
                        id,
                        iso_code_2,
                        name,
                        description,
                        region,
                        subregion
                    )
                    VALUES (
                        94,
                        'NU',
                        'Niue',
                        'Niue',
                        'Oceania',
                        'Polynesia'
                    );

INSERT INTO country (
                        id,
                        iso_code_2,
                        name,
                        description,
                        region,
                        subregion
                    )
                    VALUES (
                        95,
                        'BZ',
                        'Belize',
                        'Belize',
                        'Americas',
                        'Central America'
                    );

INSERT INTO country (
                        id,
                        iso_code_2,
                        name,
                        description,
                        region,
                        subregion
                    )
                    VALUES (
                        96,
                        'CN',
                        'China',
                        'People''s Republic of China',
                        'Asia',
                        'Eastern Asia'
                    );

INSERT INTO country (
                        id,
                        iso_code_2,
                        name,
                        description,
                        region,
                        subregion
                    )
                    VALUES (
                        97,
                        'WS',
                        'Samoa',
                        'Independent State of Samoa',
                        'Oceania',
                        'Polynesia'
                    );

INSERT INTO country (
                        id,
                        iso_code_2,
                        name,
                        description,
                        region,
                        subregion
                    )
                    VALUES (
                        98,
                        'VG',
                        'British Virgin Islands',
                        'Virgin Islands',
                        'Americas',
                        'Caribbean'
                    );

INSERT INTO country (
                        id,
                        iso_code_2,
                        name,
                        description,
                        region,
                        subregion
                    )
                    VALUES (
                        99,
                        'SD',
                        'Sudan',
                        'Republic of the Sudan',
                        'Africa',
                        'Northern Africa'
                    );

INSERT INTO country (
                        id,
                        iso_code_2,
                        name,
                        description,
                        region,
                        subregion
                    )
                    VALUES (
                        100,
                        'NF',
                        'Norfolk Island',
                        'Territory of Norfolk Island',
                        'Oceania',
                        'Australia and New Zealand'
                    );

INSERT INTO country (
                        id,
                        iso_code_2,
                        name,
                        description,
                        region,
                        subregion
                    )
                    VALUES (
                        101,
                        'SK',
                        'Slovakia',
                        'Slovak Republic',
                        'Europe',
                        'Central Europe'
                    );

INSERT INTO country (
                        id,
                        iso_code_2,
                        name,
                        description,
                        region,
                        subregion
                    )
                    VALUES (
                        102,
                        'BI',
                        'Burundi',
                        'Republic of Burundi',
                        'Africa',
                        'Eastern Africa'
                    );

INSERT INTO country (
                        id,
                        iso_code_2,
                        name,
                        description,
                        region,
                        subregion
                    )
                    VALUES (
                        103,
                        'MH',
                        'Marshall Islands',
                        'Republic of the Marshall Islands',
                        'Oceania',
                        'Micronesia'
                    );

INSERT INTO country (
                        id,
                        iso_code_2,
                        name,
                        description,
                        region,
                        subregion
                    )
                    VALUES (
                        104,
                        'AT',
                        'Austria',
                        'Republic of Austria',
                        'Europe',
                        'Central Europe'
                    );

INSERT INTO country (
                        id,
                        iso_code_2,
                        name,
                        description,
                        region,
                        subregion
                    )
                    VALUES (
                        105,
                        'MZ',
                        'Mozambique',
                        'Republic of Mozambique',
                        'Africa',
                        'Eastern Africa'
                    );

INSERT INTO country (
                        id,
                        iso_code_2,
                        name,
                        description,
                        region,
                        subregion
                    )
                    VALUES (
                        106,
                        'VC',
                        'Saint Vincent and the Grenadines',
                        'Saint Vincent and the Grenadines',
                        'Americas',
                        'Caribbean'
                    );

INSERT INTO country (
                        id,
                        iso_code_2,
                        name,
                        description,
                        region,
                        subregion
                    )
                    VALUES (
                        107,
                        'PG',
                        'Papua New Guinea',
                        'Independent State of Papua New Guinea',
                        'Oceania',
                        'Melanesia'
                    );

INSERT INTO country (
                        id,
                        iso_code_2,
                        name,
                        description,
                        region,
                        subregion
                    )
                    VALUES (
                        108,
                        'TR',
                        'Turkey',
                        'Republic of Turkey',
                        'Asia',
                        'Western Asia'
                    );

INSERT INTO country (
                        id,
                        iso_code_2,
                        name,
                        description,
                        region,
                        subregion
                    )
                    VALUES (
                        109,
                        'XK',
                        'Kosovo',
                        'Republic of Kosovo',
                        'Europe',
                        'Southeast Europe'
                    );

INSERT INTO country (
                        id,
                        iso_code_2,
                        name,
                        description,
                        region,
                        subregion
                    )
                    VALUES (
                        110,
                        'GD',
                        'Grenada',
                        'Grenada',
                        'Americas',
                        'Caribbean'
                    );

INSERT INTO country (
                        id,
                        iso_code_2,
                        name,
                        description,
                        region,
                        subregion
                    )
                    VALUES (
                        111,
                        'KH',
                        'Cambodia',
                        'Kingdom of Cambodia',
                        'Asia',
                        'South-Eastern Asia'
                    );

INSERT INTO country (
                        id,
                        iso_code_2,
                        name,
                        description,
                        region,
                        subregion
                    )
                    VALUES (
                        112,
                        'PT',
                        'Portugal',
                        'Portuguese Republic',
                        'Europe',
                        'Southern Europe'
                    );

INSERT INTO country (
                        id,
                        iso_code_2,
                        name,
                        description,
                        region,
                        subregion
                    )
                    VALUES (
                        113,
                        'GB',
                        'United Kingdom',
                        'United Kingdom of Great Britain and Northern Ireland',
                        'Europe',
                        'Northern Europe'
                    );

INSERT INTO country (
                        id,
                        iso_code_2,
                        name,
                        description,
                        region,
                        subregion
                    )
                    VALUES (
                        114,
                        'NG',
                        'Nigeria',
                        'Federal Republic of Nigeria',
                        'Africa',
                        'Western Africa'
                    );

INSERT INTO country (
                        id,
                        iso_code_2,
                        name,
                        description,
                        region,
                        subregion
                    )
                    VALUES (
                        115,
                        'AI',
                        'Anguilla',
                        'Anguilla',
                        'Americas',
                        'Caribbean'
                    );

INSERT INTO country (
                        id,
                        iso_code_2,
                        name,
                        description,
                        region,
                        subregion
                    )
                    VALUES (
                        116,
                        'MP',
                        'Northern Mariana Islands',
                        'Commonwealth of the Northern Mariana Islands',
                        'Oceania',
                        'Micronesia'
                    );

INSERT INTO country (
                        id,
                        iso_code_2,
                        name,
                        description,
                        region,
                        subregion
                    )
                    VALUES (
                        117,
                        'IL',
                        'Israel',
                        'State of Israel',
                        'Asia',
                        'Western Asia'
                    );

INSERT INTO country (
                        id,
                        iso_code_2,
                        name,
                        description,
                        region,
                        subregion
                    )
                    VALUES (
                        118,
                        'GF',
                        'French Guiana',
                        'Guiana',
                        'Americas',
                        'South America'
                    );

INSERT INTO country (
                        id,
                        iso_code_2,
                        name,
                        description,
                        region,
                        subregion
                    )
                    VALUES (
                        119,
                        'LB',
                        'Lebanon',
                        'Lebanese Republic',
                        'Asia',
                        'Western Asia'
                    );

INSERT INTO country (
                        id,
                        iso_code_2,
                        name,
                        description,
                        region,
                        subregion
                    )
                    VALUES (
                        120,
                        'JP',
                        'Japan',
                        'Japan',
                        'Asia',
                        'Eastern Asia'
                    );

INSERT INTO country (
                        id,
                        iso_code_2,
                        name,
                        description,
                        region,
                        subregion
                    )
                    VALUES (
                        121,
                        'GM',
                        'Gambia',
                        'Republic of the Gambia',
                        'Africa',
                        'Western Africa'
                    );

INSERT INTO country (
                        id,
                        iso_code_2,
                        name,
                        description,
                        region,
                        subregion
                    )
                    VALUES (
                        122,
                        'MF',
                        'Saint Martin',
                        'Saint Martin',
                        'Americas',
                        'Caribbean'
                    );

INSERT INTO country (
                        id,
                        iso_code_2,
                        name,
                        description,
                        region,
                        subregion
                    )
                    VALUES (
                        123,
                        'GW',
                        'Guinea-Bissau',
                        'Republic of Guinea-Bissau',
                        'Africa',
                        'Western Africa'
                    );

INSERT INTO country (
                        id,
                        iso_code_2,
                        name,
                        description,
                        region,
                        subregion
                    )
                    VALUES (
                        124,
                        'LA',
                        'Laos',
                        'Lao People''s Democratic Republic',
                        'Asia',
                        'South-Eastern Asia'
                    );

INSERT INTO country (
                        id,
                        iso_code_2,
                        name,
                        description,
                        region,
                        subregion
                    )
                    VALUES (
                        125,
                        'MK',
                        'North Macedonia',
                        'Republic of North Macedonia',
                        'Europe',
                        'Southeast Europe'
                    );

INSERT INTO country (
                        id,
                        iso_code_2,
                        name,
                        description,
                        region,
                        subregion
                    )
                    VALUES (
                        126,
                        'QA',
                        'Qatar',
                        'State of Qatar',
                        'Asia',
                        'Western Asia'
                    );

INSERT INTO country (
                        id,
                        iso_code_2,
                        name,
                        description,
                        region,
                        subregion
                    )
                    VALUES (
                        127,
                        'ZM',
                        'Zambia',
                        'Republic of Zambia',
                        'Africa',
                        'Eastern Africa'
                    );

INSERT INTO country (
                        id,
                        iso_code_2,
                        name,
                        description,
                        region,
                        subregion
                    )
                    VALUES (
                        128,
                        'BB',
                        'Barbados',
                        'Barbados',
                        'Americas',
                        'Caribbean'
                    );

INSERT INTO country (
                        id,
                        iso_code_2,
                        name,
                        description,
                        region,
                        subregion
                    )
                    VALUES (
                        129,
                        'VA',
                        'Vatican City',
                        'Vatican City State',
                        'Europe',
                        'Southern Europe'
                    );

INSERT INTO country (
                        id,
                        iso_code_2,
                        name,
                        description,
                        region,
                        subregion
                    )
                    VALUES (
                        130,
                        'IT',
                        'Italy',
                        'Italian Republic',
                        'Europe',
                        'Southern Europe'
                    );

INSERT INTO country (
                        id,
                        iso_code_2,
                        name,
                        description,
                        region,
                        subregion
                    )
                    VALUES (
                        131,
                        'KM',
                        'Comoros',
                        'Union of the Comoros',
                        'Africa',
                        'Eastern Africa'
                    );

INSERT INTO country (
                        id,
                        iso_code_2,
                        name,
                        description,
                        region,
                        subregion
                    )
                    VALUES (
                        132,
                        'AL',
                        'Albania',
                        'Republic of Albania',
                        'Europe',
                        'Southeast Europe'
                    );

INSERT INTO country (
                        id,
                        iso_code_2,
                        name,
                        description,
                        region,
                        subregion
                    )
                    VALUES (
                        133,
                        'GI',
                        'Gibraltar',
                        'Gibraltar',
                        'Europe',
                        'Southern Europe'
                    );

INSERT INTO country (
                        id,
                        iso_code_2,
                        name,
                        description,
                        region,
                        subregion
                    )
                    VALUES (
                        134,
                        'MN',
                        'Mongolia',
                        'Mongolia',
                        'Asia',
                        'Eastern Asia'
                    );

INSERT INTO country (
                        id,
                        iso_code_2,
                        name,
                        description,
                        region,
                        subregion
                    )
                    VALUES (
                        135,
                        'TO',
                        'Tonga',
                        'Kingdom of Tonga',
                        'Oceania',
                        'Polynesia'
                    );

INSERT INTO country (
                        id,
                        iso_code_2,
                        name,
                        description,
                        region,
                        subregion
                    )
                    VALUES (
                        136,
                        'MG',
                        'Madagascar',
                        'Republic of Madagascar',
                        'Africa',
                        'Eastern Africa'
                    );

INSERT INTO country (
                        id,
                        iso_code_2,
                        name,
                        description,
                        region,
                        subregion
                    )
                    VALUES (
                        137,
                        'PM',
                        'Saint Pierre and Miquelon',
                        'Saint Pierre and Miquelon',
                        'Americas',
                        'North America'
                    );

INSERT INTO country (
                        id,
                        iso_code_2,
                        name,
                        description,
                        region,
                        subregion
                    )
                    VALUES (
                        138,
                        'SH',
                        'Saint Helena, Ascension and Tristan da Cunha',
                        'Saint Helena, Ascension and Tristan da Cunha',
                        'Africa',
                        'Western Africa'
                    );

INSERT INTO country (
                        id,
                        iso_code_2,
                        name,
                        description,
                        region,
                        subregion
                    )
                    VALUES (
                        139,
                        'MC',
                        'Monaco',
                        'Principality of Monaco',
                        'Europe',
                        'Western Europe'
                    );

INSERT INTO country (
                        id,
                        iso_code_2,
                        name,
                        description,
                        region,
                        subregion
                    )
                    VALUES (
                        140,
                        'BR',
                        'Brazil',
                        'Federative Republic of Brazil',
                        'Americas',
                        'South America'
                    );

INSERT INTO country (
                        id,
                        iso_code_2,
                        name,
                        description,
                        region,
                        subregion
                    )
                    VALUES (
                        141,
                        'AU',
                        'Australia',
                        'Commonwealth of Australia',
                        'Oceania',
                        'Australia and New Zealand'
                    );

INSERT INTO country (
                        id,
                        iso_code_2,
                        name,
                        description,
                        region,
                        subregion
                    )
                    VALUES (
                        142,
                        'GY',
                        'Guyana',
                        'Co-operative Republic of Guyana',
                        'Americas',
                        'South America'
                    );

INSERT INTO country (
                        id,
                        iso_code_2,
                        name,
                        description,
                        region,
                        subregion
                    )
                    VALUES (
                        143,
                        'SI',
                        'Slovenia',
                        'Republic of Slovenia',
                        'Europe',
                        'Central Europe'
                    );

INSERT INTO country (
                        id,
                        iso_code_2,
                        name,
                        description,
                        region,
                        subregion
                    )
                    VALUES (
                        144,
                        'SM',
                        'San Marino',
                        'Republic of San Marino',
                        'Europe',
                        'Southern Europe'
                    );

INSERT INTO country (
                        id,
                        iso_code_2,
                        name,
                        description,
                        region,
                        subregion
                    )
                    VALUES (
                        145,
                        'TK',
                        'Tokelau',
                        'Tokelau',
                        'Oceania',
                        'Polynesia'
                    );

INSERT INTO country (
                        id,
                        iso_code_2,
                        name,
                        description,
                        region,
                        subregion
                    )
                    VALUES (
                        146,
                        'PS',
                        'Palestine',
                        'State of Palestine',
                        'Asia',
                        'Western Asia'
                    );

INSERT INTO country (
                        id,
                        iso_code_2,
                        name,
                        description,
                        region,
                        subregion
                    )
                    VALUES (
                        147,
                        'BT',
                        'Bhutan',
                        'Kingdom of Bhutan',
                        'Asia',
                        'Southern Asia'
                    );

INSERT INTO country (
                        id,
                        iso_code_2,
                        name,
                        description,
                        region,
                        subregion
                    )
                    VALUES (
                        148,
                        'SX',
                        'Sint Maarten',
                        'Sint Maarten',
                        'Americas',
                        'Caribbean'
                    );

INSERT INTO country (
                        id,
                        iso_code_2,
                        name,
                        description,
                        region,
                        subregion
                    )
                    VALUES (
                        149,
                        'PH',
                        'Philippines',
                        'Republic of the Philippines',
                        'Asia',
                        'South-Eastern Asia'
                    );

INSERT INTO country (
                        id,
                        iso_code_2,
                        name,
                        description,
                        region,
                        subregion
                    )
                    VALUES (
                        150,
                        'CL',
                        'Chile',
                        'Republic of Chile',
                        'Americas',
                        'South America'
                    );

INSERT INTO country (
                        id,
                        iso_code_2,
                        name,
                        description,
                        region,
                        subregion
                    )
                    VALUES (
                        151,
                        'MQ',
                        'Martinique',
                        'Martinique',
                        'Americas',
                        'Caribbean'
                    );

INSERT INTO country (
                        id,
                        iso_code_2,
                        name,
                        description,
                        region,
                        subregion
                    )
                    VALUES (
                        152,
                        'HT',
                        'Haiti',
                        'Republic of Haiti',
                        'Americas',
                        'Caribbean'
                    );

INSERT INTO country (
                        id,
                        iso_code_2,
                        name,
                        description,
                        region,
                        subregion
                    )
                    VALUES (
                        153,
                        'HM',
                        'Heard Island and McDonald Islands',
                        'Heard Island and McDonald Islands',
                        'Antarctic',
                        NULL
                    );

INSERT INTO country (
                        id,
                        iso_code_2,
                        name,
                        description,
                        region,
                        subregion
                    )
                    VALUES (
                        154,
                        'AQ',
                        'Antarctica',
                        'Antarctica',
                        'Antarctic',
                        NULL
                    );

INSERT INTO country (
                        id,
                        iso_code_2,
                        name,
                        description,
                        region,
                        subregion
                    )
                    VALUES (
                        155,
                        'ST',
                        'São Tomé and Príncipe',
                        'Democratic Republic of São Tomé and Príncipe',
                        'Africa',
                        'Middle Africa'
                    );

INSERT INTO country (
                        id,
                        iso_code_2,
                        name,
                        description,
                        region,
                        subregion
                    )
                    VALUES (
                        156,
                        'MO',
                        'Macau',
                        'Macao Special Administrative Region of the People''s Republic of China',
                        'Asia',
                        'Eastern Asia'
                    );

INSERT INTO country (
                        id,
                        iso_code_2,
                        name,
                        description,
                        region,
                        subregion
                    )
                    VALUES (
                        157,
                        'MU',
                        'Mauritius',
                        'Republic of Mauritius',
                        'Africa',
                        'Eastern Africa'
                    );

INSERT INTO country (
                        id,
                        iso_code_2,
                        name,
                        description,
                        region,
                        subregion
                    )
                    VALUES (
                        158,
                        'BH',
                        'Bahrain',
                        'Kingdom of Bahrain',
                        'Asia',
                        'Western Asia'
                    );

INSERT INTO country (
                        id,
                        iso_code_2,
                        name,
                        description,
                        region,
                        subregion
                    )
                    VALUES (
                        159,
                        'MX',
                        'Mexico',
                        'United Mexican States',
                        'Americas',
                        'North America'
                    );

INSERT INTO country (
                        id,
                        iso_code_2,
                        name,
                        description,
                        region,
                        subregion
                    )
                    VALUES (
                        160,
                        'PN',
                        'Pitcairn Islands',
                        'Pitcairn Group of Islands',
                        'Oceania',
                        'Polynesia'
                    );

INSERT INTO country (
                        id,
                        iso_code_2,
                        name,
                        description,
                        region,
                        subregion
                    )
                    VALUES (
                        161,
                        'AR',
                        'Argentina',
                        'Argentine Republic',
                        'Americas',
                        'South America'
                    );

INSERT INTO country (
                        id,
                        iso_code_2,
                        name,
                        description,
                        region,
                        subregion
                    )
                    VALUES (
                        162,
                        'NP',
                        'Nepal',
                        'Federal Democratic Republic of Nepal',
                        'Asia',
                        'Southern Asia'
                    );

INSERT INTO country (
                        id,
                        iso_code_2,
                        name,
                        description,
                        region,
                        subregion
                    )
                    VALUES (
                        163,
                        'SE',
                        'Sweden',
                        'Kingdom of Sweden',
                        'Europe',
                        'Northern Europe'
                    );

INSERT INTO country (
                        id,
                        iso_code_2,
                        name,
                        description,
                        region,
                        subregion
                    )
                    VALUES (
                        164,
                        'SL',
                        'Sierra Leone',
                        'Republic of Sierra Leone',
                        'Africa',
                        'Western Africa'
                    );

INSERT INTO country (
                        id,
                        iso_code_2,
                        name,
                        description,
                        region,
                        subregion
                    )
                    VALUES (
                        165,
                        'SZ',
                        'Eswatini',
                        'Kingdom of Eswatini',
                        'Africa',
                        'Southern Africa'
                    );

INSERT INTO country (
                        id,
                        iso_code_2,
                        name,
                        description,
                        region,
                        subregion
                    )
                    VALUES (
                        166,
                        'ES',
                        'Spain',
                        'Kingdom of Spain',
                        'Europe',
                        'Southern Europe'
                    );

INSERT INTO country (
                        id,
                        iso_code_2,
                        name,
                        description,
                        region,
                        subregion
                    )
                    VALUES (
                        167,
                        'CO',
                        'Colombia',
                        'Republic of Colombia',
                        'Americas',
                        'South America'
                    );

INSERT INTO country (
                        id,
                        iso_code_2,
                        name,
                        description,
                        region,
                        subregion
                    )
                    VALUES (
                        168,
                        'TC',
                        'Turks and Caicos Islands',
                        'Turks and Caicos Islands',
                        'Americas',
                        'Caribbean'
                    );

INSERT INTO country (
                        id,
                        iso_code_2,
                        name,
                        description,
                        region,
                        subregion
                    )
                    VALUES (
                        169,
                        'DJ',
                        'Djibouti',
                        'Republic of Djibouti',
                        'Africa',
                        'Eastern Africa'
                    );

INSERT INTO country (
                        id,
                        iso_code_2,
                        name,
                        description,
                        region,
                        subregion
                    )
                    VALUES (
                        170,
                        'NR',
                        'Nauru',
                        'Republic of Nauru',
                        'Oceania',
                        'Micronesia'
                    );

INSERT INTO country (
                        id,
                        iso_code_2,
                        name,
                        description,
                        region,
                        subregion
                    )
                    VALUES (
                        171,
                        'SV',
                        'El Salvador',
                        'Republic of El Salvador',
                        'Americas',
                        'Central America'
                    );

INSERT INTO country (
                        id,
                        iso_code_2,
                        name,
                        description,
                        region,
                        subregion
                    )
                    VALUES (
                        172,
                        'AX',
                        'Åland Islands',
                        'Åland Islands',
                        'Europe',
                        'Northern Europe'
                    );

INSERT INTO country (
                        id,
                        iso_code_2,
                        name,
                        description,
                        region,
                        subregion
                    )
                    VALUES (
                        173,
                        'GP',
                        'Guadeloupe',
                        'Guadeloupe',
                        'Americas',
                        'Caribbean'
                    );

INSERT INTO country (
                        id,
                        iso_code_2,
                        name,
                        description,
                        region,
                        subregion
                    )
                    VALUES (
                        174,
                        'HN',
                        'Honduras',
                        'Republic of Honduras',
                        'Americas',
                        'Central America'
                    );

INSERT INTO country (
                        id,
                        iso_code_2,
                        name,
                        description,
                        region,
                        subregion
                    )
                    VALUES (
                        175,
                        'KE',
                        'Kenya',
                        'Republic of Kenya',
                        'Africa',
                        'Eastern Africa'
                    );

INSERT INTO country (
                        id,
                        iso_code_2,
                        name,
                        description,
                        region,
                        subregion
                    )
                    VALUES (
                        176,
                        'MT',
                        'Malta',
                        'Republic of Malta',
                        'Europe',
                        'Southern Europe'
                    );

INSERT INTO country (
                        id,
                        iso_code_2,
                        name,
                        description,
                        region,
                        subregion
                    )
                    VALUES (
                        177,
                        'LV',
                        'Latvia',
                        'Republic of Latvia',
                        'Europe',
                        'Northern Europe'
                    );

INSERT INTO country (
                        id,
                        iso_code_2,
                        name,
                        description,
                        region,
                        subregion
                    )
                    VALUES (
                        178,
                        'GA',
                        'Gabon',
                        'Gabonese Republic',
                        'Africa',
                        'Middle Africa'
                    );

INSERT INTO country (
                        id,
                        iso_code_2,
                        name,
                        description,
                        region,
                        subregion
                    )
                    VALUES (
                        179,
                        'HK',
                        'Hong Kong',
                        'Hong Kong Special Administrative Region of the People''s Republic of China',
                        'Asia',
                        'Eastern Asia'
                    );

INSERT INTO country (
                        id,
                        iso_code_2,
                        name,
                        description,
                        region,
                        subregion
                    )
                    VALUES (
                        180,
                        'SJ',
                        'Svalbard and Jan Mayen',
                        'Svalbard og Jan Mayen',
                        'Europe',
                        'Northern Europe'
                    );

INSERT INTO country (
                        id,
                        iso_code_2,
                        name,
                        description,
                        region,
                        subregion
                    )
                    VALUES (
                        181,
                        'TV',
                        'Tuvalu',
                        'Tuvalu',
                        'Oceania',
                        'Polynesia'
                    );

INSERT INTO country (
                        id,
                        iso_code_2,
                        name,
                        description,
                        region,
                        subregion
                    )
                    VALUES (
                        182,
                        'TL',
                        'Timor-Leste',
                        'Democratic Republic of Timor-Leste',
                        'Asia',
                        'South-Eastern Asia'
                    );

INSERT INTO country (
                        id,
                        iso_code_2,
                        name,
                        description,
                        region,
                        subregion
                    )
                    VALUES (
                        183,
                        'EH',
                        'Western Sahara',
                        'Sahrawi Arab Democratic Republic',
                        'Africa',
                        'Northern Africa'
                    );

INSERT INTO country (
                        id,
                        iso_code_2,
                        name,
                        description,
                        region,
                        subregion
                    )
                    VALUES (
                        184,
                        'LS',
                        'Lesotho',
                        'Kingdom of Lesotho',
                        'Africa',
                        'Southern Africa'
                    );

INSERT INTO country (
                        id,
                        iso_code_2,
                        name,
                        description,
                        region,
                        subregion
                    )
                    VALUES (
                        185,
                        'US',
                        'United States',
                        'United States of America',
                        'Americas',
                        'North America'
                    );

INSERT INTO country (
                        id,
                        iso_code_2,
                        name,
                        description,
                        region,
                        subregion
                    )
                    VALUES (
                        186,
                        'TH',
                        'Thailand',
                        'Kingdom of Thailand',
                        'Asia',
                        'South-Eastern Asia'
                    );

INSERT INTO country (
                        id,
                        iso_code_2,
                        name,
                        description,
                        region,
                        subregion
                    )
                    VALUES (
                        187,
                        'IO',
                        'British Indian Ocean Territory',
                        'British Indian Ocean Territory',
                        'Africa',
                        'Eastern Africa'
                    );

INSERT INTO country (
                        id,
                        iso_code_2,
                        name,
                        description,
                        region,
                        subregion
                    )
                    VALUES (
                        188,
                        'IN',
                        'India',
                        'Republic of India',
                        'Asia',
                        'Southern Asia'
                    );

INSERT INTO country (
                        id,
                        iso_code_2,
                        name,
                        description,
                        region,
                        subregion
                    )
                    VALUES (
                        189,
                        'LT',
                        'Lithuania',
                        'Republic of Lithuania',
                        'Europe',
                        'Northern Europe'
                    );

INSERT INTO country (
                        id,
                        iso_code_2,
                        name,
                        description,
                        region,
                        subregion
                    )
                    VALUES (
                        190,
                        'MS',
                        'Montserrat',
                        'Montserrat',
                        'Americas',
                        'Caribbean'
                    );

INSERT INTO country (
                        id,
                        iso_code_2,
                        name,
                        description,
                        region,
                        subregion
                    )
                    VALUES (
                        191,
                        'ZW',
                        'Zimbabwe',
                        'Republic of Zimbabwe',
                        'Africa',
                        'Southern Africa'
                    );

INSERT INTO country (
                        id,
                        iso_code_2,
                        name,
                        description,
                        region,
                        subregion
                    )
                    VALUES (
                        192,
                        'FK',
                        'Falkland Islands',
                        'Falkland Islands',
                        'Americas',
                        'South America'
                    );

INSERT INTO country (
                        id,
                        iso_code_2,
                        name,
                        description,
                        region,
                        subregion
                    )
                    VALUES (
                        193,
                        'MV',
                        'Maldives',
                        'Republic of the Maldives',
                        'Asia',
                        'Southern Asia'
                    );

INSERT INTO country (
                        id,
                        iso_code_2,
                        name,
                        description,
                        region,
                        subregion
                    )
                    VALUES (
                        194,
                        'TN',
                        'Tunisia',
                        'Tunisian Republic',
                        'Africa',
                        'Northern Africa'
                    );

INSERT INTO country (
                        id,
                        iso_code_2,
                        name,
                        description,
                        region,
                        subregion
                    )
                    VALUES (
                        195,
                        'EE',
                        'Estonia',
                        'Republic of Estonia',
                        'Europe',
                        'Northern Europe'
                    );

INSERT INTO country (
                        id,
                        iso_code_2,
                        name,
                        description,
                        region,
                        subregion
                    )
                    VALUES (
                        196,
                        'BD',
                        'Bangladesh',
                        'People''s Republic of Bangladesh',
                        'Asia',
                        'Southern Asia'
                    );

INSERT INTO country (
                        id,
                        iso_code_2,
                        name,
                        description,
                        region,
                        subregion
                    )
                    VALUES (
                        197,
                        'UZ',
                        'Uzbekistan',
                        'Republic of Uzbekistan',
                        'Asia',
                        'Central Asia'
                    );

INSERT INTO country (
                        id,
                        iso_code_2,
                        name,
                        description,
                        region,
                        subregion
                    )
                    VALUES (
                        198,
                        'GH',
                        'Ghana',
                        'Republic of Ghana',
                        'Africa',
                        'Western Africa'
                    );

INSERT INTO country (
                        id,
                        iso_code_2,
                        name,
                        description,
                        region,
                        subregion
                    )
                    VALUES (
                        199,
                        'NO',
                        'Norway',
                        'Kingdom of Norway',
                        'Europe',
                        'Northern Europe'
                    );

INSERT INTO country (
                        id,
                        iso_code_2,
                        name,
                        description,
                        region,
                        subregion
                    )
                    VALUES (
                        200,
                        'SO',
                        'Somalia',
                        'Federal Republic of Somalia',
                        'Africa',
                        'Eastern Africa'
                    );

INSERT INTO country (
                        id,
                        iso_code_2,
                        name,
                        description,
                        region,
                        subregion
                    )
                    VALUES (
                        201,
                        'BS',
                        'Bahamas',
                        'Commonwealth of the Bahamas',
                        'Americas',
                        'Caribbean'
                    );

INSERT INTO country (
                        id,
                        iso_code_2,
                        name,
                        description,
                        region,
                        subregion
                    )
                    VALUES (
                        202,
                        'OM',
                        'Oman',
                        'Sultanate of Oman',
                        'Asia',
                        'Western Asia'
                    );

INSERT INTO country (
                        id,
                        iso_code_2,
                        name,
                        description,
                        region,
                        subregion
                    )
                    VALUES (
                        203,
                        'LU',
                        'Luxembourg',
                        'Grand Duchy of Luxembourg',
                        'Europe',
                        'Western Europe'
                    );

INSERT INTO country (
                        id,
                        iso_code_2,
                        name,
                        description,
                        region,
                        subregion
                    )
                    VALUES (
                        204,
                        'IQ',
                        'Iraq',
                        'Republic of Iraq',
                        'Asia',
                        'Western Asia'
                    );

INSERT INTO country (
                        id,
                        iso_code_2,
                        name,
                        description,
                        region,
                        subregion
                    )
                    VALUES (
                        205,
                        'VI',
                        'United States Virgin Islands',
                        'Virgin Islands of the United States',
                        'Americas',
                        'Caribbean'
                    );

INSERT INTO country (
                        id,
                        iso_code_2,
                        name,
                        description,
                        region,
                        subregion
                    )
                    VALUES (
                        206,
                        'MR',
                        'Mauritania',
                        'Islamic Republic of Mauritania',
                        'Africa',
                        'Western Africa'
                    );

INSERT INTO country (
                        id,
                        iso_code_2,
                        name,
                        description,
                        region,
                        subregion
                    )
                    VALUES (
                        207,
                        'CA',
                        'Canada',
                        'Canada',
                        'Americas',
                        'North America'
                    );

INSERT INTO country (
                        id,
                        iso_code_2,
                        name,
                        description,
                        region,
                        subregion
                    )
                    VALUES (
                        208,
                        'MM',
                        'Myanmar',
                        'Republic of the Union of Myanmar',
                        'Asia',
                        'South-Eastern Asia'
                    );

INSERT INTO country (
                        id,
                        iso_code_2,
                        name,
                        description,
                        region,
                        subregion
                    )
                    VALUES (
                        209,
                        'MY',
                        'Malaysia',
                        'Malaysia',
                        'Asia',
                        'South-Eastern Asia'
                    );

INSERT INTO country (
                        id,
                        iso_code_2,
                        name,
                        description,
                        region,
                        subregion
                    )
                    VALUES (
                        210,
                        'CC',
                        'Cocos (Keeling) Islands',
                        'Territory of the Cocos (Keeling) Islands',
                        'Oceania',
                        'Australia and New Zealand'
                    );

INSERT INTO country (
                        id,
                        iso_code_2,
                        name,
                        description,
                        region,
                        subregion
                    )
                    VALUES (
                        211,
                        'BQ',
                        'Caribbean Netherlands',
                        'Bonaire, Sint Eustatius and Saba',
                        'Americas',
                        'Caribbean'
                    );

INSERT INTO country (
                        id,
                        iso_code_2,
                        name,
                        description,
                        region,
                        subregion
                    )
                    VALUES (
                        212,
                        'UG',
                        'Uganda',
                        'Republic of Uganda',
                        'Africa',
                        'Eastern Africa'
                    );

INSERT INTO country (
                        id,
                        iso_code_2,
                        name,
                        description,
                        region,
                        subregion
                    )
                    VALUES (
                        213,
                        'IR',
                        'Iran',
                        'Islamic Republic of Iran',
                        'Asia',
                        'Southern Asia'
                    );

INSERT INTO country (
                        id,
                        iso_code_2,
                        name,
                        description,
                        region,
                        subregion
                    )
                    VALUES (
                        214,
                        'CW',
                        'Curaçao',
                        'Country of Curaçao',
                        'Americas',
                        'Caribbean'
                    );

INSERT INTO country (
                        id,
                        iso_code_2,
                        name,
                        description,
                        region,
                        subregion
                    )
                    VALUES (
                        215,
                        'RO',
                        'Romania',
                        'Romania',
                        'Europe',
                        'Southeast Europe'
                    );

INSERT INTO country (
                        id,
                        iso_code_2,
                        name,
                        description,
                        region,
                        subregion
                    )
                    VALUES (
                        216,
                        'SY',
                        'Syria',
                        'Syrian Arab Republic',
                        'Asia',
                        'Western Asia'
                    );

INSERT INTO country (
                        id,
                        iso_code_2,
                        name,
                        description,
                        region,
                        subregion
                    )
                    VALUES (
                        217,
                        'FJ',
                        'Fiji',
                        'Republic of Fiji',
                        'Oceania',
                        'Melanesia'
                    );

INSERT INTO country (
                        id,
                        iso_code_2,
                        name,
                        description,
                        region,
                        subregion
                    )
                    VALUES (
                        218,
                        'AW',
                        'Aruba',
                        'Aruba',
                        'Americas',
                        'Caribbean'
                    );

INSERT INTO country (
                        id,
                        iso_code_2,
                        name,
                        description,
                        region,
                        subregion
                    )
                    VALUES (
                        219,
                        'NL',
                        'Netherlands',
                        'Kingdom of the Netherlands',
                        'Europe',
                        'Western Europe'
                    );

INSERT INTO country (
                        id,
                        iso_code_2,
                        name,
                        description,
                        region,
                        subregion
                    )
                    VALUES (
                        220,
                        'PE',
                        'Peru',
                        'Republic of Peru',
                        'Americas',
                        'South America'
                    );

INSERT INTO country (
                        id,
                        iso_code_2,
                        name,
                        description,
                        region,
                        subregion
                    )
                    VALUES (
                        221,
                        'RE',
                        'Réunion',
                        'Réunion Island',
                        'Africa',
                        'Eastern Africa'
                    );

INSERT INTO country (
                        id,
                        iso_code_2,
                        name,
                        description,
                        region,
                        subregion
                    )
                    VALUES (
                        222,
                        'BW',
                        'Botswana',
                        'Republic of Botswana',
                        'Africa',
                        'Southern Africa'
                    );

INSERT INTO country (
                        id,
                        iso_code_2,
                        name,
                        description,
                        region,
                        subregion
                    )
                    VALUES (
                        223,
                        'AF',
                        'Afghanistan',
                        'Islamic Republic of Afghanistan',
                        'Asia',
                        'Southern Asia'
                    );

INSERT INTO country (
                        id,
                        iso_code_2,
                        name,
                        description,
                        region,
                        subregion
                    )
                    VALUES (
                        224,
                        'RS',
                        'Serbia',
                        'Republic of Serbia',
                        'Europe',
                        'Southeast Europe'
                    );

INSERT INTO country (
                        id,
                        iso_code_2,
                        name,
                        description,
                        region,
                        subregion
                    )
                    VALUES (
                        225,
                        'CZ',
                        'Czechia',
                        'Czech Republic',
                        'Europe',
                        'Central Europe'
                    );

INSERT INTO country (
                        id,
                        iso_code_2,
                        name,
                        description,
                        region,
                        subregion
                    )
                    VALUES (
                        226,
                        'DM',
                        'Dominica',
                        'Commonwealth of Dominica',
                        'Americas',
                        'Caribbean'
                    );

INSERT INTO country (
                        id,
                        iso_code_2,
                        name,
                        description,
                        region,
                        subregion
                    )
                    VALUES (
                        227,
                        'PL',
                        'Poland',
                        'Republic of Poland',
                        'Europe',
                        'Central Europe'
                    );

INSERT INTO country (
                        id,
                        iso_code_2,
                        name,
                        description,
                        region,
                        subregion
                    )
                    VALUES (
                        228,
                        'BJ',
                        'Benin',
                        'Republic of Benin',
                        'Africa',
                        'Western Africa'
                    );

INSERT INTO country (
                        id,
                        iso_code_2,
                        name,
                        description,
                        region,
                        subregion
                    )
                    VALUES (
                        229,
                        'MD',
                        'Moldova',
                        'Republic of Moldova',
                        'Europe',
                        'Eastern Europe'
                    );

INSERT INTO country (
                        id,
                        iso_code_2,
                        name,
                        description,
                        region,
                        subregion
                    )
                    VALUES (
                        230,
                        'RU',
                        'Russia',
                        'Russian Federation',
                        'Europe',
                        'Eastern Europe'
                    );

INSERT INTO country (
                        id,
                        iso_code_2,
                        name,
                        description,
                        region,
                        subregion
                    )
                    VALUES (
                        231,
                        'BL',
                        'Saint Barthélemy',
                        'Collectivity of Saint Barthélemy',
                        'Americas',
                        'Caribbean'
                    );

INSERT INTO country (
                        id,
                        iso_code_2,
                        name,
                        description,
                        region,
                        subregion
                    )
                    VALUES (
                        232,
                        'ID',
                        'Indonesia',
                        'Republic of Indonesia',
                        'Asia',
                        'South-Eastern Asia'
                    );

INSERT INTO country (
                        id,
                        iso_code_2,
                        name,
                        description,
                        region,
                        subregion
                    )
                    VALUES (
                        233,
                        'NI',
                        'Nicaragua',
                        'Republic of Nicaragua',
                        'Americas',
                        'Central America'
                    );

INSERT INTO country (
                        id,
                        iso_code_2,
                        name,
                        description,
                        region,
                        subregion
                    )
                    VALUES (
                        234,
                        'AM',
                        'Armenia',
                        'Republic of Armenia',
                        'Asia',
                        'Western Asia'
                    );

INSERT INTO country (
                        id,
                        iso_code_2,
                        name,
                        description,
                        region,
                        subregion
                    )
                    VALUES (
                        235,
                        'BY',
                        'Belarus',
                        'Republic of Belarus',
                        'Europe',
                        'Eastern Europe'
                    );

INSERT INTO country (
                        id,
                        iso_code_2,
                        name,
                        description,
                        region,
                        subregion
                    )
                    VALUES (
                        236,
                        'ET',
                        'Ethiopia',
                        'Federal Democratic Republic of Ethiopia',
                        'Africa',
                        'Eastern Africa'
                    );

INSERT INTO country (
                        id,
                        iso_code_2,
                        name,
                        description,
                        region,
                        subregion
                    )
                    VALUES (
                        237,
                        'CR',
                        'Costa Rica',
                        'Republic of Costa Rica',
                        'Americas',
                        'Central America'
                    );

INSERT INTO country (
                        id,
                        iso_code_2,
                        name,
                        description,
                        region,
                        subregion
                    )
                    VALUES (
                        238,
                        'JO',
                        'Jordan',
                        'Hashemite Kingdom of Jordan',
                        'Asia',
                        'Western Asia'
                    );

INSERT INTO country (
                        id,
                        iso_code_2,
                        name,
                        description,
                        region,
                        subregion
                    )
                    VALUES (
                        239,
                        'DE',
                        'Germany',
                        'Federal Republic of Germany',
                        'Europe',
                        'Western Europe'
                    );

INSERT INTO country (
                        id,
                        iso_code_2,
                        name,
                        description,
                        region,
                        subregion
                    )
                    VALUES (
                        240,
                        'EC',
                        'Ecuador',
                        'Republic of Ecuador',
                        'Americas',
                        'South America'
                    );

INSERT INTO country (
                        id,
                        iso_code_2,
                        name,
                        description,
                        region,
                        subregion
                    )
                    VALUES (
                        241,
                        'KP',
                        'North Korea',
                        'Democratic People''s Republic of Korea',
                        'Asia',
                        'Eastern Asia'
                    );

INSERT INTO country (
                        id,
                        iso_code_2,
                        name,
                        description,
                        region,
                        subregion
                    )
                    VALUES (
                        242,
                        'IS',
                        'Iceland',
                        'Iceland',
                        'Europe',
                        'Northern Europe'
                    );

INSERT INTO country (
                        id,
                        iso_code_2,
                        name,
                        description,
                        region,
                        subregion
                    )
                    VALUES (
                        243,
                        'SS',
                        'South Sudan',
                        'Republic of South Sudan',
                        'Africa',
                        'Middle Africa'
                    );

INSERT INTO country (
                        id,
                        iso_code_2,
                        name,
                        description,
                        region,
                        subregion
                    )
                    VALUES (
                        244,
                        'MW',
                        'Malawi',
                        'Republic of Malawi',
                        'Africa',
                        'Eastern Africa'
                    );

INSERT INTO country (
                        id,
                        iso_code_2,
                        name,
                        description,
                        region,
                        subregion
                    )
                    VALUES (
                        245,
                        'BF',
                        'Burkina Faso',
                        'Burkina Faso',
                        'Africa',
                        'Western Africa'
                    );

INSERT INTO country (
                        id,
                        iso_code_2,
                        name,
                        description,
                        region,
                        subregion
                    )
                    VALUES (
                        246,
                        'CD',
                        'DR Congo',
                        'Democratic Republic of the Congo',
                        'Africa',
                        'Middle Africa'
                    );

INSERT INTO country (
                        id,
                        iso_code_2,
                        name,
                        description,
                        region,
                        subregion
                    )
                    VALUES (
                        247,
                        'VE',
                        'Venezuela',
                        'Bolivarian Republic of Venezuela',
                        'Americas',
                        'South America'
                    );

INSERT INTO country (
                        id,
                        iso_code_2,
                        name,
                        description,
                        region,
                        subregion
                    )
                    VALUES (
                        248,
                        'BN',
                        'Brunei',
                        'Nation of Brunei, Abode of Peace',
                        'Asia',
                        'South-Eastern Asia'
                    );

INSERT INTO country (
                        id,
                        iso_code_2,
                        name,
                        description,
                        region,
                        subregion
                    )
                    VALUES (
                        249,
                        'PY',
                        'Paraguay',
                        'Republic of Paraguay',
                        'Americas',
                        'South America'
                    );

INSERT INTO country (
                        id,
                        iso_code_2,
                        name,
                        description,
                        region,
                        subregion
                    )
                    VALUES (
                        250,
                        'BG',
                        'Bulgaria',
                        'Republic of Bulgaria',
                        'Europe',
                        'Southeast Europe'
                    );


COMMIT TRANSACTION;
PRAGMA foreign_keys = on;
