{% macro get_chain_tvl_columns() %}

    {% set query %}
        SELECT column_name
        FROM information_schema.columns
        WHERE table_schema = 'raw_defillama'
          AND table_name = 'protocols'
          AND column_name LIKE 'chain_tvls__%'
        ORDER BY column_name
    {% endset %}

    {% set results = run_query(query) %}

    {% if execute %}
        {% set columns = results.columns[0].values() %}
    {% else %}
        {% set columns = [] %}
    {% endif %}

    {{ return(columns) }}

{% endmacro %}