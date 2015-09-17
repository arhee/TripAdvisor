review_schema = """
		CREATE TABLE IF NOT EXISTS Vietnam (
		Key TEXT PRIMARY KEY,
		Country TEXT,
		ItemReviewed TEXT,
		Type TEXT,
		ParentGroup TEXT,
		Location TEXT,
		Rating INT,
		Review TEXT,
		ReviewDate TEXT,
		VisitDate TEXT,
		Title TEXT,
		UID INT,
		ReviewID TEXT,
		User TEXT,
		UserHome TEXT
		)"""