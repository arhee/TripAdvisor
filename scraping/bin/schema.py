vietnam_schema = """
		CREATE TABLE IF NOT EXISTS vietnam (
		key TEXT PRIMARY KEY,
		country TEXT,
		item_reviewed TEXT,
		type TEXT,
		parent_group TEXT,
		location TEXT,
		rating INT,
		item_url TEXT,
		review TEXT,
		review_date TEXT,
		visit_date TEXT,
		title TEXT,
		uid INT,
		reviewID TEXT,
		user TEXT,
		user_home TEXT
		)"""

review_schema = """
		CREATE TABLE IF NOT EXISTS attractions (
		url TEXT PRIMARY KEY,
		name TEXT,
		coe INT,
		choice_award INT,
		rank INT,
		country TEXT,
		type TEXT,
		location TEXT)"""